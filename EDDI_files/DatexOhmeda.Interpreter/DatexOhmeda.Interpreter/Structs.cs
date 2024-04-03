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
using System.Runtime.InteropServices;

namespace DatexOhmeda.Interpreter
{
    [AttributeUsage(AttributeTargets.Field)]
    public class PrimaryData : System.Attribute
    {
    }

    [StructLayout(LayoutKind.Explicit, Pack = 1)]
    public unsafe struct DO_record
    {
        [FieldOffset(0)]
        public fixed byte buffer[1490];
        [FieldOffset(0)]
        public DO_hdr hdr;
        [FieldOffset(40)]
        public fixed byte data[1450];
    }

    public enum dri_main_type
    {
        DRI_MT_PHDB,
        DRI_MT_WAVE,
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct DO_hdr
    {
        public short r_len;
        public byte r_nbr;
        public byte dri_level;
        public ushort plug_id;
        public uint r_time;
        public byte n_subnet;
        public byte res;
        public ushort dest_plug_id;
        public ushort r_maintype;
        public sr_desc sr_desc_0;
        public sr_desc sr_desc_1;
        public sr_desc sr_desc_2;
        public sr_desc sr_desc_3;
        public sr_desc sr_desc_4;
        public sr_desc sr_desc_5;
        public sr_desc sr_desc_6;
        public sr_desc sr_desc_7;

        public sr_desc sr_desc(int n)
        {
            switch (n)
            {
                case 0: return sr_desc_0;
                case 1: return sr_desc_1;
                case 2: return sr_desc_2;
                case 3: return sr_desc_3;
                case 4: return sr_desc_4;
                case 5: return sr_desc_5;
                case 6: return sr_desc_6;
                default: return sr_desc_7;
            }
        }

        public DateTime Time
        {
            get
            {
                DateTime rtime = new DateTime(1970, 1, 1, 0, 0, 0);
                return rtime.AddSeconds(r_time);
            }
        }
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct sr_desc
    {
        public short sr_offset;
        public byte sr_type;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct dri_phdb_req
    {
        public byte phdb_rcrd_type;
        public short tx_interval;
        public long phdb_class_bf;
        public short reserved;
    }

    public enum dri_ph_subtype
    {
        DRI_PH_REQUEST,
        DRI_PH_DISPL,
        DRI_PH_10S_TREND,
        DRI_PH_60S_TREND,
        DRI_PH_AUX_INFO,
        DRI_PH_TREND_CONTROL,
        DRI_PH_TREND_REQUEST,
        DRI_PH_END_OF_SUBRECORDS = 0xff,
    }

    public enum dri_ph_class
    {
        DRI_PH_BASIC,
        DRI_PH_EXT1,
        DRI_PH_EXT2,
        DRI_PH_EXT3,
        DRI_PH_AUX,
    }

    public enum dri_phdbcl_req_mask
    {
        DRI_PHDBCL_REQ_BASIC = 0xFFFE, // first bit is unset, use with & operator
        DRI_PHDBCL_DENY_BASIC = 0x0001,
        DRI_PHDBCL_REQ_EXT1 = 0x0002,
        DRI_PHDBCL_REQ_EXT2 = 0x0004,
        DRI_PHDBCL_REQ_EXT3 = 0X0008,
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct dri_phdb
    {
        public uint time;
        public dri_phdb_data data;
        public byte marker;
        public byte pdm_ctrl_bf;
        public ushort cl_drilvl_subt;
    }

    [StructLayout(LayoutKind.Explicit, Pack = 1)]
    public struct dri_phdb_data
    {
        [FieldOffset(0)]
        public basic_phdb basic;
        [FieldOffset(0)]
        public ext1_phdb ext1;
        [FieldOffset(0)]
        public ext2_phdb ext2;
        [FieldOffset(0)]
        public ext3_phdb ext3;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct group_hdr
    {
        public uint status;
        public ushort label;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct basic_phdb
    {
        public ecg_group ecg;
        public p_group p1;
        public p_group p2;
        public p_group p3;
        public p_group p4;
        public nibp_group nibp;
        public t_group t1;
        public t_group t2;
        public t_group t3;
        public t_group t4;
        public spo2_pl_group spo2;
        public co2_group co2;
        public o2_group o2;
        public n2o_group n2o;
        public aa_group aa;
        public flow_vol_group flow_vol;
        public co_wedge_group co_wedge;
        public nmt_group nmt;
        public ecg_extra_group ecg_extra;
        public svo2_group svo2;
        public p_group p5;
        public p_group p6;
        fixed byte reserved[2];
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct ecg_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short hr;
        [PrimaryData]
        public short st1;
        [PrimaryData]
        public short st2;
        [PrimaryData]
        public short st3;
        [PrimaryData]
        public short imp_rr;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct p_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short sys;
        [PrimaryData]
        public short dia;
        [PrimaryData]
        public short mean;
        [PrimaryData]
        public short hr;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct nibp_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short sys;
        [PrimaryData]
        public short dia;
        [PrimaryData]
        public short mean;
        [PrimaryData]
        public short hr;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct t_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short temp;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct spo2_pl_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short SpO2;
        [PrimaryData]
        public short pr;
        [PrimaryData]
        public short ir_amp;
        public short SvO2;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct co2_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short et;
        [PrimaryData]
        public short fi;
        [PrimaryData]
        public short rr;
        [PrimaryData]
        public short amb_press;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct o2_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short et;
        [PrimaryData]
        public short fi;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct n2o_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short et;
        [PrimaryData]
        public short fi;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct aa_group
    {
        public group_hdr hdr;
        [PrimaryData]
        public short et;
        [PrimaryData]
        public short fi;
        [PrimaryData]
        public short mac_sum;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct flow_vol_group
    {
        public group_hdr hdr;
        public short rr;
        public short ppeak;
        public short peep;
        public short pplat;
        public short tv_insp;
        public short tv_exp;
        public short compliance;
        public short mv_exp;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct co_wedge_group
    {
        public group_hdr hdr;
        public short co;
        public short blood_temp;
        public short rhef;
        public short pcwp;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct nmt_group
    {
        public group_hdr hdr;
        public short t1;
        public short tratio;
        public short ptc;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct ecg_extra_group
    {
        public short hr_ecg;
        public short hr_max;
        public short hr_min;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct svo2_group
    {
        public group_hdr hdr;
        public short svo2;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct ext1_phdb
    {
        fixed byte ecg[48]; // arrh_ecg_group not defined
        public ecg_12_group ecg12;
        fixed byte reserved[192];
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct ecg_12_group
    {
        public group_hdr hdr;
        public short stI;
        public short stII;
        public short stIII;
        public short stAVL;
        public short stAVR;
        public short stAVF;
        public short stV1;
        public short stV2;
        public short stV3;
        public short stV4;
        public short stV5;
        public short stV6;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct ext2_phdb
    {
        public nmt2_group nmt2;
        public eeg_group eeg;
        fixed byte reserved[174];
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct nmt2_group
    {
        public group_hdr hdr;
        public short count;
        public short nmt_t1;
        public short nmt_t2;
        public short nmt_t3;
        public short nmt_t4;
        short nmt_resv1;
        short nmt_resv2;
        short nmt_resv3;
        short nmt_resv4;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct eeg_group
    {
        public group_hdr hdr;
        public short femg;
        public eeg_channel eeg1;
        public eeg_channel eeg2;
        public eeg_channel eeg3;
        public eeg_channel eeg4;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct eeg_channel
    {
        public short ampl;
        public short sef;
        public short mf;
        public short delta_proc;
        public short theta_proc;
        public short alpha_proc;
        public short beta_proc;
        public short bsr;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct ext3_phdb
    {
        public gasex_group gasex;
        public flow_vol_group2 flow_vol2;
        public bal_gas_group bal;
        public tono_group tono;
        fixed byte reserved[178];
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct gasex_group
    {
        public group_hdr hdr;
        public short vo2;
        public short vco2;
        public short ee;
        public short rq;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct flow_vol_group2
    {
        public group_hdr hdr;
        public short ipeep;
        public short pmean;
        public short raw;
        public short mv_insp;
        public short epeep;
        public short mv_spont;
        public short ie_ratio;
        public short insp_time;
        public short exp_time;
        public short static_compliance;
        public short static_pplat;
        public short static_peepe;
        public short static_peepi;
        fixed short reserved[7];
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct bal_gas_group
    {
        public group_hdr hdr;
        public short et;
        public short fi;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct tono_group
    {
        public group_hdr hdr;
        public short prco2;
        public short pr_et;
        public short pr_pa;
        public short pa_delay;
        public short phi;
        public short phi_delay;
        public short amb_press;
        public short cpma;
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct aux_phdb_info
    {
        public uint nibp_time;
        public short cuff_press;
        public uint co_time;
        public uint pcwp_time;
        public short pat_bsa;
        public short ecg_display_size;
        public short spo2_display_size;
        public short invp1_display_size;
        public short invp2_display_size;
        public short invp3_display_size;
        public short invp4_display_size;
        public short resp_display_size;
        public short co2_scale;
        public short o2_scale;
        public short n2o_scale;
        public short aa_scale;
        short reserved2_scale;
        public short flow_scale;
        short reserved_scale;
        public short awp_scale;
        public short bp_unit;
        public short co2_unit;
        public short temp_unit;
        public short awp_unit;
        public short flow_unit;
        public short ie_unit;
        public short o2_display_offset;
        short reserved_field;
        public ushort misc_bits;
        public short invp5_display_size;
        public short invp6_display_size;
        public ushort old_or_new_gasmod;
        public short prco2_unit;
        public int prco2_age;
        public uint static_peep_time;
        public short eeg_scale;
        public short pvc_shown;
        fixed byte reserved[30];
    }

    public enum dri_wf_subtype
    {
        DRI_WF_CMD,
        DRI_WF_ECG1,
        DRI_WF_ECG2,
        DRI_WF_ECG3,
        DRI_WF_INVP1,
        DRI_WF_INVP2,
        DRI_WF_INVP3,
        DRI_WF_INVP4,
        DRI_WF_PLETH,
        DRI_WF_CO2,
        DRI_WF_O2,
        DRI_WF_N2O,
        DRI_WF_AA,
        DRI_WF_AWP,
        DRI_WF_FLOW,
        DRI_WF_RESP,
        DRI_WF_INVP5,
        DRI_WF_INVP6,
        DRI_WF_EEG1,
        DRI_WF_EEG2,
        DRI_WF_EEG3,
        DRI_WF_EEG4,
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public unsafe struct wf_req
    {
        public short req_type;
        public short secs;
        public fixed byte type[8];
        public fixed byte addl_type[2 * 8];
        public fixed short reserved[10];
    }

    public enum dri_wf_req
    {
        WF_REQ_CONT_START,
        WF_REQ_CONT_STOP,
        WF_REQ_TIMED_START,
    }

    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct wf_hdr
    {
        public short act_len;
        public ushort status;
        public ushort label;
    }
}
