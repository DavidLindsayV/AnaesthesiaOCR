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
 * Developer : Adam Langley
 * Date : 01/01/2011
 */

// this class has been deprecated. See StreamAnalysis.DampedTraceNode
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Harrison.DatexOhmeda.Interpreter
{
    public class DampedTraceMonitor
    {
        public event EventHandler<DampedTraceEventArgs> DampedTraceAlert;

        public class DampedTraceEventArgs : EventArgs
        {
            public AlertReasons AlertReason
            { get; private set; }

            public DampedTraceEventArgs(AlertReasons reason)
            {
                this.AlertReason = reason;
            }
        }

        public enum AlertReasons
        {
            None,
            MprIncreased,
            MprExceedsLimit
        }

        protected virtual void OnDampedTraceAlert(AlertReasons reason)
        {
            if (null != DampedTraceAlert)
                DampedTraceAlert(this, new DampedTraceEventArgs(reason));
        }

        public void Enqueue(double p1_mean, double p1_sys, double p1_dia)
        {
            double map = 0;
            double pp = 0;
            AlertReasons alertReason = AlertReasons.None;
            double mpr = 0;

            try
            {
                if (p1_mean > 40 && p1_mean < 130)
                {
                    map = p1_mean;
                    pp = p1_sys - p1_dia;
                }
                else
                {
                    map = AVERAGE_MAP;
                    pp = AVERAGE_PP;
                }

                if (_medianPP.Count < 5 || _medianMap.Count < 5)
                    return;

                if (_medianMap.Median / _medianPP.Median > 3)
                    mpr = 1;
                else
                    mpr = _medianMap.Median / _medianPP.Median;

                // ignore '0' _previousMpr for first sample
                if (_previousMpr > 0 && mpr > _previousMpr)
                    _increaseCount++;
                else
                    _increaseCount = 0;

                if (mpr > (map * 0.02) + 0.7)
                    _mprExceedsCount++;
                else
                    _mprExceedsCount = 0;

                if (3 < _mprExceedsCount)
                    alertReason = AlertReasons.MprExceedsLimit;

                if (_increaseCount > (12 + 3))
                    alertReason = AlertReasons.MprIncreased;

                _previousMpr = mpr;

                if (AlertReasons.None != alertReason)
                    OnDampedTraceAlert(alertReason);
            }
            finally
            {
                _medianMap.Enqueue(map);
                _medianPP.Enqueue(pp);
            }
        }

        private MedianQueue<double> _medianMap = new MedianQueue<double>(5);
        private MedianQueue<double> _medianPP = new MedianQueue<double>(5);
        private const int AVERAGE_MAP = 81;
        private const int AVERAGE_PP = 57;
        private double _previousMpr = -1;
        private int _increaseCount;
        private int _mprExceedsCount = 0;
    }
}
