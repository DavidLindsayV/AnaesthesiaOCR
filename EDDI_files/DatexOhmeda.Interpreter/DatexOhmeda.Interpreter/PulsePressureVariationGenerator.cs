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

// this class is Deprecated: see StreamAnalysis.PpvNode
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Harrison.DatexOhmeda.Interpreter
{
    public class PulsePressureVariationGenerator
    {
        //private int _sampleCount = 0;
        private int _sampleSize = 0;
        private int _minSamples = 0;
        private MaxMinQueue pressureMinMax = new MaxMinQueue();
        private MaxMinQueue pulsePressureMinMax = new MaxMinQueue();

        public event EventHandler PulsePressureVariationChanged;
        public event EventHandler PulsePressureExtentsChanged;
        public event EventHandler PressureExtentsChanged;
        
        public MaxMinQueue PressureMinMax
        {
            get { return pressureMinMax; }
        }
        

        public MaxMinQueue PulsePressureMinMax
        {
            get { return pulsePressureMinMax; }
        }

        public PulsePressureVariationGenerator(int sampleSize = 200, int minSamples = 5)
        {
            this._sampleSize = sampleSize;
            this._minSamples = 5;
        }

        protected virtual void OnPulsePressureVariationChanged()
        {
            if (null != PulsePressureVariationChanged)
                PulsePressureVariationChanged(this, EventArgs.Empty);
        }

        protected virtual void OnPulsePressureExtentsChanged()
        {
            if (null != PulsePressureExtentsChanged)
                PulsePressureExtentsChanged(this, EventArgs.Empty);
        }

        protected virtual void OnPressureExtentsChanged()
        {
            if (null != PressureExtentsChanged)
                PressureExtentsChanged(this, EventArgs.Empty);
        }

        public bool Enqueue(short pressure)
        {
            pressureMinMax.Enqueue(pressure);
            OnPressureExtentsChanged();

            if (pressureMinMax.Count == _sampleSize)
            {
                // we have received enough samples to generate a ppv

                pulsePressureMinMax.Enqueue(((double)pressureMinMax.Maximum / 100) - ((double)pressureMinMax.Minimum / 100));
                OnPulsePressureExtentsChanged();

                pressureMinMax.Reset();
                OnPressureExtentsChanged();
            }

            if (pulsePressureMinMax.Count == _minSamples)
            {
                PulsePressureVariation = 100 * (pulsePressureMinMax.Maximum - pulsePressureMinMax.Minimum) / (pulsePressureMinMax.Maximum + pulsePressureMinMax.Minimum) / 2;
                
                OnPulsePressureVariationChanged();
                pulsePressureMinMax.Reset();
                OnPulsePressureExtentsChanged();
                return true;
            }

            return false;
        }

        public double PulsePressureVariation
        { get; private set; }
    }
}
