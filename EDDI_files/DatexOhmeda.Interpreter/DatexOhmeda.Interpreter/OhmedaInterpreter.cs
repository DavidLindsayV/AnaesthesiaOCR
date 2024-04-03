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

namespace DatexOhmeda.Interpreter
{
    public class OhmedaInterpreter : IDisposable
    {
        public event EventHandler<RecordEventArgs> RecordArrived;

        protected virtual void OnRecordArrived(RecordEventArgs args)
        {
            var tempHandler = RecordArrived;
            if (null != tempHandler)
                tempHandler(this, args);
        }

        private bool isControl = false;
        const byte FLAG_CONTROL = 0x7d;
        const byte FLAG_DELIMIT = 0x7e;
        const byte FLAG_CONTROL_ENCODED = 0x5d;
        const byte FLAG_DELIMIT_ENCODED = 0x5e;
        private List<byte> buf = new List<byte>();

        ///// <summary>
        ///// Record arrivals will not be immediately signalled, but will instead be appended to an internal queue.
        ///// Call to 'Flush' will fire event for each record in queue, and clear queue.
        ///// </summary>
        //public bool QueueEvents
        //{
        //    get;
        //    set;
        //}

        public int SourceFrameCount
        {
            get;
            private set;
        }

        public OhmedaInterpreter()
        {
        }

        /// <summary>
        /// Processes an array of bytes, utilising as much as possible to construct full DO records.
        /// </summary>
        /// <param name="buffer"></param>
        public void Enqueue(byte[] buffer)
        {
            foreach (var item in buffer)
                Enqueue(item);
        }

        public void Enqueue(byte item)
        {

            switch (item)
            {
                //case -1:
                //    Disconnect();
                //    break; // end of file, no more data
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
                        buf.Add((byte)item);
                    break;
                case FLAG_DELIMIT_ENCODED: // reset control flag if necessary
                    if (isControl)
                    {
                        buf.Add(FLAG_DELIMIT);
                        isControl = false;
                    }
                    else
                        buf.Add((byte)item);
                    break;
                default: // add data to buffer
                    buf.Add((byte)item);
                    break;
            }
        }

        private void ProcessFrame(List<byte> in_buf)
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

                    DO_record in_rec = StructUtil.ReadStruct<DO_record>(buf, 0);
                    SourceFrameCount++;


                    DateTime rtime = new DateTime(1970, 1, 1, 0, 0, 0);
                    rtime = rtime.AddSeconds(in_rec.hdr.r_time);

                    if (in_rec.hdr.r_maintype == (ushort)dri_main_type.DRI_MT_PHDB)
                    {
                        //m_textOutHeader = "rtime";
                        //m_textOutBuffer = rtime.ToString("G");

                        ProcessPhdbRecord(in_rec);

                        // relay if this is requested
                        //if (comRelayPort.IsOpen && m_relayRequestReceived)
                        //{
                        //    unsafe
                        //    {
                        //        // send the record
                        //        DOMonitor.WriteFrame(in_rec.buffer, in_rec.hdr.r_len, comRelayPort.BaseStream);
                        //        AddLogMessage("Relayed phdb.rtime=" + rtime.ToString("G"));
                        //    }
                        //    m_relayRequestReceived = false;

                        //}

                        // write phdb record to text file, if requested
                        //if (chkSaveText.Checked && m_textOut != null)
                        //{
                        //    try
                        //    {
                        //        if (!m_textOutHeaderWritten)
                        //        {
                        //            m_textOut.WriteLine(m_textOutHeader);
                        //            m_textOutHeaderWritten = true;
                        //        }
                        //        m_textOut.WriteLine(m_textOutBuffer);
                        //    }
                        //    catch (IOException ex)
                        //    {
                        //        FileStream fs = m_dofOut;
                        //        m_dofOut = null;
                        //        fs.Close();
                        //        AddLogMessage(ex.Message);
                        //    }
                        //}

                    }
                    else if (in_rec.hdr.r_maintype == (ushort)dri_main_type.DRI_MT_WAVE)
                    {
                        ProcessWaveRecord(in_rec);
                    }
                    // trigger event
                    //if (OnRecordReceived != null)
                    //    try
                    //    {
                    //        OnRecordReceived(rcd);
                    //    }
                    //    catch (ObjectDisposedException)
                    //    {
                    //    }
                }
            }

            // clear ready for next frame
            in_buf.Clear();
        }

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

        public void Dispose()
        {

        }
    }
}
