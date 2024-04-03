/*
 * THIS SOFTWARE IS PROVIDED BY 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, 
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BE LIABLE 
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Author: Adam Langley
 * Date : 01/01/2011
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.IO;

namespace DatexOhmeda.Interpreter
{
    public delegate void RecordDelegate(DO_record in_rcd);

    public class DOMonitor : IDisposable
    {
        public event EventHandler<RecordEventArgs> RecordArrived;

        public event EventHandler ReadTerminated = null;

        protected virtual void OnRecordArrived(RecordEventArgs args)
        {
            var tempHandler = RecordArrived;
            if (null != tempHandler)
                tempHandler(this, args);
        }

        public event EventHandler<EventArgs> ValidConnection;
        protected virtual void OnValidConnection(EventArgs e)
        {
            var tempHandler = ValidConnection;
            if (null != tempHandler)
                tempHandler(this, e);
        }

        public bool Connection
        {
            get { return _ValidConnection; }
            private set { _ValidConnection = value; }
        }


        const int FLAG_CONTROL = 0x7d;
        const int FLAG_DELIMIT = 0x7e;
        const int FLAG_CONTROL_ENCODED = 0x5d;
        const int FLAG_DELIMIT_ENCODED = 0x5e;

        //public event RecordDelegate OnRecordReceived;

        Stream m_source;
        int m_sourceFrameCount = 0;

        bool m_readThreadAbort;
        Thread m_readThread;
        ManualResetEvent m_readFlag;


        public DOMonitor()
        {
            m_readThreadAbort = false;
            m_readFlag = new ManualResetEvent(false);
            m_readThread = new Thread(new ThreadStart(ReadThreadProc));
            m_readThread.Start();
        }

        public void Dispose()
        {
            m_readFlag.Reset();
            m_readThreadAbort = true;
        }

        public void Connect(Stream in_source)
        {
            Disconnect();
            m_source = in_source;
            m_sourceFrameCount = 0;
            m_readFlag.Set();
        }

        public void Connect()
        {
            Disconnect();
            m_readFlag.Set();
        }

        public void Disconnect()
        {
            m_readFlag.Reset();
            System.Threading.Thread.Sleep(500);
            if (m_source != null)
                m_source.Close();
        }

        public void SendWaveRequest(dri_wf_subtype[] in_types, short in_duration)
        {
            // the request record to send
            DO_record rcd;
            rcd.hdr.r_maintype = (ushort)dri_main_type.DRI_MT_WAVE;
            short reqlen;
            unsafe
            {
                reqlen = (short)sizeof(wf_req);
                rcd.hdr.r_len = (short)(sizeof(DO_hdr)); // set up length as length of header only, will be modified later
            }

            // setup the first subrecord, which is to stop any transmissions
            rcd.hdr.sr_desc_0.sr_offset = 0;
            rcd.hdr.sr_desc_0.sr_type = (byte)dri_wf_subtype.DRI_WF_CMD;


            wf_req req = new wf_req(); // zero everything, including reserved fields
            req.req_type = (short)dri_wf_req.WF_REQ_CONT_STOP; // stop all transmissions
            unsafe
            {
                StructUtil.WriteStruct<wf_req>(req, rcd.data, 0);
            }

            // second subrecord is to select waveforms
            if (in_types != null && in_types.Length > 0)
                unsafe
                {
                    req.req_type = in_duration > 0 ? (short)dri_wf_req.WF_REQ_TIMED_START : (short)dri_wf_req.WF_REQ_CONT_START;
                    req.secs = in_duration;
                    for (int n = 0; n < Math.Min(in_types.Length, 8); n++)
                        req.type[n] = (byte)in_types[n];
                    if (in_types.Length < 8)
                        req.type[in_types.Length] = (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS;
                    else
                    {
                        for (int n = 8; n < Math.Min(in_types.Length, 16); n++)
                            req.addl_type[n - 8] = (byte)in_types[n];
                        if (in_types.Length < 24)
                            req.addl_type[in_types.Length - 8] = (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS;
                    }
                    unsafe
                    {
                        StructUtil.WriteStruct<wf_req>(req, rcd.data, 0);
                    }
                    // setup terminal record and overall length
                    rcd.hdr.sr_desc_2.sr_type = (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS;
                    rcd.hdr.r_len += (short)(2 * reqlen);
                }
            else
            {
                // setup terminal record and overall length
                rcd.hdr.sr_desc_1.sr_offset = reqlen;
                rcd.hdr.sr_desc_1.sr_type = (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS;
                rcd.hdr.r_len += (short)(reqlen);
            }

            unsafe
            {
                // finally, send the request
                WriteFrame(rcd.buffer, rcd.hdr.r_len, m_source);
            }

        }

        public void SendPhdbRequest(dri_ph_subtype in_type, short in_interval, dri_ph_class[] in_class)
        {
            // the request record to send
            DO_record rcd;
            rcd.hdr.r_maintype = (ushort)dri_main_type.DRI_MT_PHDB;

            bool wantAux = false;  // whether there is a request for auxiliary info, which must be handled differently 
            short reqlen;
            unsafe
            {
                reqlen = (short)sizeof(dri_phdb_req);
                rcd.hdr.r_len = (short)(sizeof(DO_hdr)); // set up length as length of header only, will be modified later
            }

            // common initialisation
            dri_phdb_req req = default(dri_phdb_req);
            req.reserved = 0; // fully initialize struct
            req.phdb_rcrd_type = (byte)in_type;
            req.tx_interval = in_interval; // same interval is used for all requests

            /* 20160528: Adam Langley */
            /* Fix for Carescape b850 - cannot send cancel request in same packet */
            /* BEGIN: Send request to CANCEL ALL in a separate request */
            // initialise and write the first subrecord, which is to stop any transmissions
            rcd.hdr.sr_desc_0.sr_offset = 0;
            rcd.hdr.sr_desc_0.sr_type = (byte)dri_ph_subtype.DRI_PH_REQUEST; // first request is cancel all phdb requests
            req.phdb_class_bf = (long)dri_phdbcl_req_mask.DRI_PHDBCL_DENY_BASIC; // default is to deny basic, as well as everything else
            unsafe
            {
                StructUtil.WriteStruct<dri_phdb_req>(req, rcd.data, 0);
            }
            unsafe
            {
                // finally, send the request
                WriteFrame(rcd.buffer, rcd.hdr.r_len, m_source);
            }
            /* END: Send request to CANCEL ALL in a separate request */

            // now set up the next subrecord, which is to request basic, ext1 - ext3 subtypes
            rcd.hdr.sr_desc_0.sr_offset = reqlen;
            rcd.hdr.sr_desc_0.sr_type = (byte)dri_ph_subtype.DRI_PH_REQUEST; // second request sets up what we want
            // set up class bitfield
            // if nothing is specified this record ends up the same as the first (i.e. stop transmissions)
            foreach (dri_ph_class cl in in_class)
            {
                switch (cl)
                {
                    case dri_ph_class.DRI_PH_BASIC:
                        req.phdb_class_bf &= (long)dri_phdbcl_req_mask.DRI_PHDBCL_REQ_BASIC;
                        break;
                    case dri_ph_class.DRI_PH_EXT1:
                        req.phdb_class_bf |= (long)dri_phdbcl_req_mask.DRI_PHDBCL_REQ_EXT1;
                        break;
                    case dri_ph_class.DRI_PH_EXT2:
                        req.phdb_class_bf |= (long)dri_phdbcl_req_mask.DRI_PHDBCL_REQ_EXT2;
                        break;
                    case dri_ph_class.DRI_PH_EXT3:
                        req.phdb_class_bf |= (long)dri_phdbcl_req_mask.DRI_PHDBCL_REQ_EXT3;
                        break;
                    case dri_ph_class.DRI_PH_AUX:
                        wantAux = true;
                        break;
                }
            }
            unsafe
            {
                StructUtil.WriteStruct<dri_phdb_req>(req, rcd.data, rcd.hdr.sr_desc_0.sr_offset);
            }

            // set the third subrecord, depending on whether aux is requested
            if (wantAux)
            {
                rcd.hdr.sr_desc_1.sr_offset = (short)(2 * reqlen);
                rcd.hdr.sr_desc_1.sr_type = (byte)dri_ph_subtype.DRI_PH_REQUEST; // second request sets up what we want
                req.phdb_rcrd_type = (byte)dri_ph_subtype.DRI_PH_AUX_INFO;
                req.phdb_class_bf = 0; // doesn't really matter for aux 
                unsafe
                {
                    StructUtil.WriteStruct<dri_phdb_req>(req, rcd.data, rcd.hdr.sr_desc_1.sr_offset);
                }
                // setup terminal record and overall length
                rcd.hdr.sr_desc_2.sr_type = (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS;
                rcd.hdr.r_len += (short)(3 * reqlen);
            }
            else {
                // setup terminal record and overall length
                rcd.hdr.sr_desc_1.sr_type = (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS;
                rcd.hdr.r_len += (short)(2 * reqlen);
            }

            unsafe
            {
                // finally, send the request
                WriteFrame(rcd.buffer, rcd.hdr.r_len, m_source);
            }
        }

        static void EncodeByte(byte in_byte, List<byte> in_encoded)
        {
            switch (in_byte)
            {
                case FLAG_DELIMIT:
                    in_encoded.Add(FLAG_CONTROL);
                    in_encoded.Add(FLAG_DELIMIT_ENCODED);
                    break;
                case FLAG_CONTROL:
                    in_encoded.Add(FLAG_CONTROL);
                    in_encoded.Add(FLAG_CONTROL_ENCODED);
                    break;
                default:
                    in_encoded.Add(in_byte);
                    break;
            }
        }

        public static unsafe void WriteFrame(byte* in_frame, int in_length, Stream in_output)
        {
            List<byte> buf = new List<byte>();

            byte checksum = 0;

            // first write the start of frame 
            buf.Add(FLAG_DELIMIT);
            // then encode the frame
            for (int n = 0; n < in_length; n++)
            {
                byte b = in_frame[n];
                EncodeByte(b, buf);
                checksum += b; // calculate checksum
            }
            // add the checksum (encode if necessary)
            EncodeByte(checksum, buf);
            // add the end-of-frame character
            buf.Add(FLAG_DELIMIT);

            // actually write the frame to the stream
            byte[] ary = buf.ToArray();
            in_output.Write(ary, 0, ary.Length);
        }

        public int SourceFrameCount
        {
            get
            {
                return m_sourceFrameCount;
            }
        }

        void ReadThreadProc()
        {
            bool isControl = false;
            List<byte> buf = new List<byte>();

            while (!m_readThreadAbort)
            {
                if (m_readFlag.WaitOne(500, true))
                {
                    // received signal
                    if (m_readThreadAbort)
                        break;

                    // try to read from source
                    int b;
                    try
                    {
                        b = m_source.ReadByte();
                    }
                    catch (IOException)
                    {
                        // m_source has been made invalid in some way, i.e. end of file, no more data
                        b = -1;
                    }

                    // received signal
                    if (m_readThreadAbort)
                        break;

                    switch (b)
                    {
                        case -1:
                            Disconnect();
                            break; // end of file, no more data
                        case FLAG_CONTROL: // special handling of the next character
                            isControl = true;
                            break;
                        case FLAG_DELIMIT: // finish or start of a frame
                            ProcessFrame(buf);
                            break;
                        case FLAG_CONTROL_ENCODED: // reset control flag if necessary
                            if (isControl)
                            {
                                buf.Add(FLAG_CONTROL);
                                isControl = false;
                            }
                            else
                                buf.Add((byte)b);
                            break;
                        case FLAG_DELIMIT_ENCODED: // reset control flag if necessary
                            if (isControl)
                            {
                                buf.Add(FLAG_DELIMIT);
                                isControl = false;
                            }
                            else
                                buf.Add((byte)b);
                            break;
                        default: // add data to buffer
                            buf.Add((byte)b);
                            break;
                    }
                }
                else
                {
                    // read flag was not raised, reset control signals
                    isControl = false;
                }
            }

            if (null != ReadTerminated)
                ReadTerminated(this, EventArgs.Empty);
        }

        void ProcessFrame(List<byte> in_buf)
        {
            int minSize = 40;
            unsafe { minSize = sizeof(DO_hdr); }
            if (in_buf.Count > minSize)
            {
                // enough data to make up a valid frame to process
                byte[] buf = in_buf.ToArray();

                // check the checksum
                byte checksum = 0;
                for (int n = 0; n < buf.Length - 1; n++)
                    checksum += buf[n];
                if (checksum == buf[buf.Length - 1])
                {
                    // trim the checksum off the end
                    Array.Resize<byte>(ref buf, buf.Length - 1);

                    DO_record rcd = StructUtil.ReadStruct<DO_record>(buf, 0);
                    m_sourceFrameCount++;

                    DateTime rtime = new DateTime(1970, 1, 1, 0, 0, 0);
                    rtime = rtime.AddSeconds(rcd.hdr.r_time);

                    if(!Connection)
                    {
                        OnValidConnection(new EventArgs());
                        Connection = true;
                    }
                   
                    if (rcd.hdr.r_maintype == (ushort)dri_main_type.DRI_MT_PHDB)
                    {
                        ProcessPhdbRecord(rcd);
                    }
                    else if (rcd.hdr.r_maintype == (ushort)dri_main_type.DRI_MT_WAVE)
                    {
                        ProcessWaveRecord(rcd);
                    }
                }
            }

            // clear ready for next frame
            in_buf.Clear();
        }

        private bool _ValidConnection;

        #region PHDB Processing
        private unsafe void ProcessPhdbRecord(DO_record in_rec)
        {
            for (int n = 0; n < 8; n++)
            {
                sr_desc sr_desc = in_rec.hdr.sr_desc(n);
                if (sr_desc.sr_type != (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS)
                    ProcessPhdbSubrecord(in_rec, sr_desc.sr_type, in_rec.data + sr_desc.sr_offset);
                else
                    break;
            }
        }

        private unsafe void ProcessPhdbSubrecord(DO_record in_rec, byte in_sr_type, byte* in_data)
        {
            switch (in_sr_type)
            {
                case (byte)dri_ph_subtype.DRI_PH_10S_TREND:
                case (byte)dri_ph_subtype.DRI_PH_60S_TREND:
                case (byte)dri_ph_subtype.DRI_PH_DISPL:
                    dri_phdb phdb = StructUtil.ReadStruct<dri_phdb>(in_data, 0);

                    DateTime rtime = new DateTime(1970, 1, 1, 0, 0, 0);
                    rtime = rtime.AddSeconds(phdb.time);


                    //ProcessPhdbData(phdb);
                    OnRecordArrived(new RecordEventArgs(in_rec, phdb));
                    break;
                case (byte)dri_ph_subtype.DRI_PH_AUX_INFO:
                    aux_phdb_info aux = StructUtil.ReadStruct<aux_phdb_info>(in_data, 0);
                    OnRecordArrived(new RecordEventArgs(in_rec, aux));
                    break;
                case (byte)dri_ph_subtype.DRI_PH_REQUEST:
                    break;

            }
        }
        #endregion

        #region WAVE Processing
        private unsafe void ProcessWaveRecord(DO_record in_rec)
        {
            for (int n = 0; n < 8; n++)
            {
                sr_desc sr_desc = in_rec.hdr.sr_desc(n);
                if (sr_desc.sr_type != (byte)dri_ph_subtype.DRI_PH_END_OF_SUBRECORDS)
                    ProcessWaveSubrecord(in_rec, sr_desc.sr_type, in_rec.data + sr_desc.sr_offset);
                else
                    break;
            }
        }

        private unsafe void ProcessWaveSubrecord(DO_record in_rec, byte in_sr_type, byte* in_data)
        {
            switch (in_sr_type)
            {
                case (byte)dri_wf_subtype.DRI_WF_CMD:
                    break;
                default:
                    wf_hdr hdr = StructUtil.ReadStruct<wf_hdr>(in_data, 0);
                    short[] data = new short[hdr.act_len];
                    int dataOffset = sizeof(wf_hdr);
                    StructUtil.ReadShortArray(in_data, dataOffset, ref data);

                    // display data
                    //ProcessData(m_dataWaves[in_sr_type], hdr);
                    //SaveWaveData(m_dataWaves[in_sr_type], data);
                    //SetChartData(m_dataWaves[in_sr_type], data);

                    //// send data to clients
                    //m_server.WriteWaveformLine(in_sr_type, hdr, data);
                    OnRecordArrived(new RecordEventArgs(in_rec, data));
                    break;
            }
        }
        #endregion
    }

}
