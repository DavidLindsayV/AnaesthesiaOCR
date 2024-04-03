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

// This class is deprecated: see StreamAnalysis.VentilationAllowsPpvNode
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Harrison.DatexOhmeda.Interpreter
{
    public class DeterminationOfVentilation
    {
        public bool IsIntermediatePositivePressureVentilated(double co2_rr, double co2_et, double co2_fi)
        {
            bool result = false;

            result = result || (3.8 <= co2_rr && co2_rr <= 12.8
                                &&
                                19.8 <= co2_et && co2_et <= 39.7
                                &&
                                co2_fi < 0.81);

            result = result || (10 <= co2_rr && co2_rr <= 12.2
                                &&
                                co2_fi < 0.16);

            result = result || (3.8 <= co2_rr && co2_rr <= 12.3
                                &&
                                19.9 <= co2_et && co2_et <= 37.7);

            return result;
        }

        public bool IsSpontaneouslyVentilated(double co2_rr, double co2_et, double co2_fi)
        {
            bool result = false;

            result = result ||  (co2_et >= 42.33 && co2_fi >= 1.0);

            result = result || (co2_rr >= 13.1
                                ||
                                (3.8 <= co2_rr && co2_rr <= 6.9));

            result = result || (co2_fi >= 1.11);

            return result;
        }

        public bool IsVentilationAppropriate(double co2_rr, double co2_et, double co2_fi)
        {
            return IsIntermediatePositivePressureVentilated(co2_rr, co2_et, co2_fi)
                    &&
                    !IsSpontaneouslyVentilated(co2_rr, co2_et, co2_fi);
        }
    }
}
