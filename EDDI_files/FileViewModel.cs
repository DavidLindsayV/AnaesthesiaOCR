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
using Caliburn.Micro;
using System.IO.Ports;
using Microsoft.Win32;
using System.IO;
using Castle.MicroKernel;
using Castle.MicroKernel.Registration;
using System.Threading;
using Eddi.Windows.Services;
using System.Text.RegularExpressions;
using Eddi.Windows.ViewModels;
using Eddi.Core.DataModels;
using Eddi.Windows.Properties;
using Eddi.Windows.ViewModels.Contracts;
using Eddi.Core;
using Eddi.Engine;
using Eddi.Engine.Models;

namespace Eddi.Windows.ViewModels.MonitorConfig
{
    class FileViewModel : Screen, IMonitorConfig
    {
        public event EventHandler DataTerminated;
        public event EventHandler Connected;

        public string GetName() { return "File"; }

        public string SelectedFile
        {
            get { return _file; }
            set { _file = value; NotifyOfPropertyChange("SelectedFile"); NotifyOfPropertyChange("CanMoveNext"); }
        }

        public double PlaybackSpeed
        {
            get { return _playbackSpeed; }
            set { _playbackSpeed = value; NotifyOfPropertyChange("PlaybackSpeed"); }
        }

        public string FileError
        {
            get { return _fileError; }
            set
            {
                _fileError = value;
                NotifyOfPropertyChange("FileError");
                NotifyOfPropertyChange("IsFileInvalid");
                NotifyOfPropertyChange("CanMoveNext");
            }
        }

        public bool IsFileInvalid
        {
            get { return null != FileError; }
        }

        public FileViewModel(
            IKernel kernel,
            ILog log,
            IEngine engine)
        {
            _kernel = kernel;
            _log = log;
            _engine = engine;

            DisplayName = "File (CSV)";

            PlaybackSpeed = 50;
        }

        public void Next()
        {
            _kernel.Register(Component.For<IMonitorConfig>().Named("monitor").Instance(this));
        }

        public void Retry()
        {
            ValidateFile();
        }

        public void Connect()
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "CSV files|*.csv";
            if (openFileDialog.ShowDialog() == true) //at this part the exception is thrown
            {
                SelectedFile = openFileDialog.FileName;
                //Stream stream = (Stream)openFileDialog.File.OpenRead();
                //byte[] bytes = new byte[stream.Length];
                //stream.Read(bytes, 0, (int)stream.Length);
            }
            ValidateFile();
        }

        public bool GetConnected()
        {
            return _Connected;
        }

        private void ValidateFile()
        {
            try
            {
                // open file and verify contents
                using (var reader = new StreamReader(File.OpenRead(SelectedFile)))
                {
                    var row = 0;
                    string line = reader.ReadLine(); // skip column headings

                    var columnNames = line.Split(',');
                    for (int i = 0; i < columnNames.Length; i++)
                        columnNames[i] = columnNames[i].Trim('"');

                    // read CSV data
                    CsvColumn COL_CO2_ET = CsvColumn.Find(columnNames, "co2.et");//new CsvColumn("AH");
                    CsvColumn COL_BP_SYS = CsvColumn.Find(columnNames, "p1.sys"); ;//new CsvColumn("G");
                    CsvColumn COL_BP_DIA = CsvColumn.Find(columnNames, "p1.dia"); ;//new CsvColumn("H");
                    CsvColumn COL_BP_MEAN = CsvColumn.Find(columnNames, "p1.mean"); ;//new CsvColumn("I");
                    CsvColumn COP_NIBP_SYS = CsvColumn.Find(columnNames, "nibp.sys"); ;
                    CsvColumn COL_NIBP_DIA = CsvColumn.Find(columnNames, "nibp.dia"); ;
                    CsvColumn COL_NIBP_MEAN = CsvColumn.Find(columnNames, "nibp.mean"); ;
                    CsvColumn COL_ECG_HR = CsvColumn.Find(columnNames, "ecg.hr"); ;//new CsvColumn("B");
                    CsvColumn COL_P1_HR = CsvColumn.Find(columnNames, "p1.hr"); ;//new CsvColumn("B");
                    CsvColumn COL_NIBP_HR = CsvColumn.Find(columnNames, "nibp.hr"); 
                    CsvColumn COL_SPO2 = CsvColumn.Find(columnNames, "spo2.spO2"); ;//new csvColumn();
                    CsvColumn COL_SPO2_HR = CsvColumn.Find(columnNames, "spo2.pr"); ;//new CsvColumn("B");
                    CsvColumn COL_PV = CsvColumn.Find(columnNames, "spo2.ir_amp"); ;//new CsvColumn("AG"); // spo2.ir_amp
                    CsvColumn COL_AA_MAC_SUM = CsvColumn.Find(columnNames, "aa.mac_sum"); ;//new CsvColumn("AR");
                    CsvColumn COL_TEMP = CsvColumn.Find(columnNames, "t1.temp"); ;//new CsvColumn("AA");
                    CsvColumn COL_CO2_FI = CsvColumn.Find(columnNames, "co2.fi"); ;//new CsvColumn("AI");
                    CsvColumn COL_CO2_RR = CsvColumn.Find(columnNames, "co2.rr"); ;//new CsvColumn("AJ");
                    CsvColumn COL_PPV;
                    CsvColumn.TryFind(columnNames, "ppv", out COL_PPV);

                    DateTime _dtTimeOfLastPHDB;

                    line = reader.ReadLine();

                    string[] columns = line.Split(',');

                    string dateString = columns[0].Trim('\"');

                    if (!DateTime.TryParseExact(columns[0].Trim('\"'), new string[] { "dd/MM/yyyy HH:mm:ss", "dd/MM/yyyy H:mm:ss", "d/MM/yyyy HH:mm:ss", "d/MM/yyyy H:mm:ss" }, System.Globalization.CultureInfo.InvariantCulture, System.Globalization.DateTimeStyles.None, out _dtTimeOfLastPHDB))
                    {
                        _log.Warn("Validating CSV file - unable to parse date-time using exact format kind. '{0}'", columns[0].Trim('\"'));
                        FileError = "Invalid CSV format. Please ensure Time column is in format dd/MM/yyyy HH:mm:ss";
                    }
                    else
                        FileError = null;
                    _Connected = true;
                    this.Connected(this, EventArgs.Empty);
                }
            }
            catch (IOException)
            {
                _log.Warn("Unable to open file. Please ensure it is not being used by another application.");
                FileError = "Unable to open file. Please ensure it is not being used by another application.";
            }
            catch (ArgumentNullException)
			{
                _log.Warn("No File Selected");
                FileError = "No File Selected";
			}
        }

        public bool CanMoveNext
        {
            get
            {
                return !string.IsNullOrWhiteSpace(SelectedFile) && null == FileError;
            }
        }

        public void Start()
        {
            if (null == _alertTimer)
            {
                _alertTimer = new Thread(TimerCallback)
                {
                    IsBackground = true
                };
                _isEndingOperation = false;
                _alertTimer.Start();
            }

        }

        public void Stop()
        {
            if(_alertTimer != null)
            {
                _alertTimer.Abort();
                _alertTimer = null;
            }
            _isEndingOperation = true;
        }

        public void TimerCallback(object state)
        {

            using (var reader = new StreamReader(File.OpenRead(SelectedFile)))
            {
                var row = 0;
                string line = reader.ReadLine(); // skip column headings

                var columnNames = line.Split(',');
                for (int i = 0; i < columnNames.Length; i++)
                    columnNames[i] = columnNames[i].Trim('"');

                // read CSV data
                CsvColumn COL_CO2_ET = CsvColumn.Find(columnNames, "co2.et");//new CsvColumn("AH");
                CsvColumn COL_BP_SYS = CsvColumn.Find(columnNames, "p1.sys"); ;//new CsvColumn("G");
                CsvColumn COL_BP_DIA = CsvColumn.Find(columnNames, "p1.dia"); ;//new CsvColumn("H");
                CsvColumn COL_BP_MEAN = CsvColumn.Find(columnNames, "p1.mean"); ;//new CsvColumn("I");
                CsvColumn COL_NIBP_SYS = CsvColumn.Find(columnNames, "nibp.sys"); ;
                CsvColumn COL_NIBP_DIA = CsvColumn.Find(columnNames, "nibp.dia"); ;
                CsvColumn COL_NIBP_MEAN = CsvColumn.Find(columnNames, "nibp.mean"); ;
                CsvColumn COL_ECG_HR = CsvColumn.Find(columnNames, "ecg.hr"); ;//new CsvColumn("B");
                CsvColumn COL_P1_HR = CsvColumn.Find(columnNames, "p1.hr"); ;//new CsvColumn("B");
                CsvColumn COL_NIBP_HR = CsvColumn.Find(columnNames, "nibp.hr"); ;//new CsvColumn
                CsvColumn COL_SPO2 = CsvColumn.Find(columnNames, "spo2.spO2"); ;//new csvColumn();
                CsvColumn COL_SPO2_HR = CsvColumn.Find(columnNames, "spo2.pr"); ;//new CsvColumn("B");
                CsvColumn COL_PV = CsvColumn.Find(columnNames, "spo2.ir_amp"); ;//new CsvColumn("AG"); // spo2.ir_amp
                CsvColumn COL_AA_MAC_SUM = CsvColumn.Find(columnNames, "aa.mac_sum"); ;//new CsvColumn("AR");
                CsvColumn COL_TEMP = CsvColumn.Find(columnNames, "t1.temp"); ;//new CsvColumn("AA");
                CsvColumn COL_CO2_FI = CsvColumn.Find(columnNames, "co2.fi"); ;//new CsvColumn("AI");
                CsvColumn COL_CO2_RR = CsvColumn.Find(columnNames, "co2.rr"); ;//new CsvColumn("AJ");
                CsvColumn COL_PPV;
                CsvColumn.TryFind(columnNames, "ppv", out COL_PPV);

                while (!_isEndingOperation && (line = reader.ReadLine()) != null)
                {
                    row++;
                    string[] columns = line.Split(',');

                    //if (columns.Length != 52)
                    //{
                    //    System.Windows.MessageBox.Show("52 columns are expected in sample data file. Stopping operation.");
                    //    return;
                    //}

                    double co2_et = 0;
                    int co2_fi = 0;
                    int co2_rr = 0;
                    int bp_sys = 0;
                    int bp_dia = 0;
                    int bp_mean = 0;
                    int nibp_sys = 0;
                    int nibp_dia = 0;
                    int nibp_mean = 0;
                    int hr_ecg = 0;
                    int hr_p1 = 0;
                    int hr_spo2 = 0;
                    int spo2_spO2 = 0;
                    double pv = 0;
                    int aa_mac_sum = 0;
                    int temp = 0;
                    double ppv = 0;

                    if (!COL_CO2_ET.TryRead(columns, out co2_et) || -32767 == co2_et)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}", COL_CO2_ET.ColumnName, row);
                        //continue;
                    }

                    if (!COL_CO2_FI.TryRead(columns, out co2_fi) || -32767 == co2_fi)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_CO2_FI.ColumnName, row);
                        //continue;
                    }

                    if (!COL_CO2_RR.TryRead(columns, out co2_rr) || -32767 == co2_rr)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_CO2_RR.ColumnName, row);
                        //continue;
                    }

                    if (!COL_BP_SYS.TryRead(columns, out bp_sys) || -32767 == bp_sys)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_BP_SYS.ColumnName, row);
                        //continue;
                    }

                    if (!COL_BP_DIA.TryRead(columns, out bp_dia) || -32767 == bp_dia)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_BP_DIA.ColumnName, row);
                        //continue;
                    }

                    if (!COL_BP_MEAN.TryRead(columns, out bp_mean) || -32767 == bp_mean)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_BP_MEAN.ColumnName, row);
                        //continue;
                    }

                    if(!COL_NIBP_SYS.TryRead(columns, out nibp_sys) || -32767 == nibp_sys)
                    {

                    }

                    if(!COL_NIBP_DIA.TryRead(columns, out nibp_dia) || -32767 == nibp_dia)
                    {

                    }

                    if(!COL_NIBP_MEAN.TryRead(columns, out nibp_mean) || -32767 == nibp_mean)
                    {

                    }

                    if (!COL_ECG_HR.TryRead(columns, out hr_ecg) || -32767 == hr_ecg)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_ECG_HR.ColumnName, row);
                        //continue;
                    }

                    if (!COL_P1_HR.TryRead(columns, out hr_p1) || -32767 == hr_p1)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_P1_HR.ColumnName, row);
                        //continue;
                    }

                    if (!COL_SPO2_HR.TryRead(columns, out hr_spo2) || -32767 == hr_spo2)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_SPO2_HR.ColumnName, row);
                        //continue;
                    }

                    if(!COL_SPO2.TryRead(columns, out spo2_spO2) || -32767 == spo2_spO2)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_SPO2.ColumnName, row);
                        //continue;
                    }

                    if (!COL_PV.TryRead(columns, out pv) || -32767 == pv)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_PV.ColumnName, row);
                        //continue;
                    }

                    if (!COL_AA_MAC_SUM.TryRead(columns, out aa_mac_sum) || -32767 == aa_mac_sum)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_AA_MAC_SUM.ColumnName, row);
                        //continue;
                    }

                    if (!COL_TEMP.TryRead(columns, out temp) || -32767 == temp)
                    {
                        _log.Warn("Column unavailable, unable to parse column {0} on row {1}, or value was outside of legal range.", COL_TEMP.ColumnName, row);
                        //continue;
                    }

                    if (null != COL_PPV)
                        double.TryParse(columns[COL_PPV.ColumnArrayIndex].Trim('"'), out ppv);

                    //TimeOfLastPHDB = columns[0];
                    DateTime _dtTimeOfLastPHDB;
                    string dateString = columns[0].Trim('\"');

                    //if (!DateTime.TryParse(dateString, out _dtTimeOfLastPHDB))
                    //{
                    //  _log.Warn("Unable to parse date-time using first format kind. '{0}'", columns[0].Trim('\"'));


                    if (!DateTime.TryParseExact(columns[0].Trim('\"'), new string[] { "dd/MM/yyyy HH:mm:ss", "dd/MM/yyyy H:mm:ss", "d/MM/yyyy HH:mm:ss", "d/MM/yyyy H:mm:ss","dd/MM/yyyy HH:mm" }, System.Globalization.CultureInfo.InvariantCulture, System.Globalization.DateTimeStyles.None, out _dtTimeOfLastPHDB))
                    {
                        _log.Warn("Unable to parse date-time using exact format kind. '{0}'", columns[0].Trim('\"'));
                    }
                    else
                        NLogLogger.SampleTime = _dtTimeOfLastPHDB;
                    //}

                    //var medianHeartRate = Harrison.StreamAnalysis.ExtensionMethods.MedianWhereAboveZero(hr_p1, hr_ecg, hr_spo2);
                    if (DateTime.MinValue != _dtTimeOfLastPHDB)
                    {

                        //update
                        _engine.Execute(_dtTimeOfLastPHDB,
                            bp_sys/100.0,
                            bp_dia/100.0,
                            bp_mean/100.0,
                            nibp_sys/100.0,
                            nibp_dia/100.0,
                            nibp_mean/100.0,
                            (short)hr_p1,
                            (short)hr_ecg,
                            (double)co2_et / 100, 
                            (double)co2_fi / 100, 
                            (short)co2_rr,
                            (short)hr_spo2,
                            spo2_spO2,
                            pv,
                            (double)aa_mac_sum / 100,
                            (double)temp / 100,
                            ppv);

                        //IMPLEMENT INV BP
                        //_engine.Execute(_dtTimeOfLastPHDB, invasiveBloodPressure, noninvasiveBloodPressure, heartRate, (double)pv / 100, (double)co2_et / 100, (double)co2_fi / 100, co2_rr,spo2_spO2, (double)aa_mac_sum / 100, (double)temp / 100, ppv);
                    }
                    Thread.Sleep((int)(10000 / PlaybackSpeed));
                }
            }

            if (null != this.DataTerminated)
                DataTerminated(this, EventArgs.Empty);
        }

        /// <summary>
        /// Flags the termination of the operation
        /// </summary>
        private bool _isEndingOperation = false;


        /// <summary>
        /// Timer for pumping demo data
        /// </summary>
        private Thread _alertTimer;

        private IKernel _kernel;
        private string _file;
        private double _playbackSpeed = 1;
        private IEngine _engine;
        private readonly ILog _log;
        private string _fileError;

        private bool _Connected;
    }
}
