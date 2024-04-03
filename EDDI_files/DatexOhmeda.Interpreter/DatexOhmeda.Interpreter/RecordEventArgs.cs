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
    public class RecordEventArgs : EventArgs
    {
        public DO_record Record
        { get; private set; }

        public dri_phdb PhdbData
        { get; private set; }

        public aux_phdb_info AuxiliaryPhdbData
        { get; private set; }

        public short[] WaveDate
        { get; private set; }

        public RecordEventArgs(DO_record record, dri_phdb phdbData)
        {
            this.Record = record;
            this.PhdbData = phdbData;
        }

        public RecordEventArgs(DO_record record, aux_phdb_info auxiliaryPhdbData)
        {
            this.Record = record;
            this.AuxiliaryPhdbData = auxiliaryPhdbData;
        }

        public RecordEventArgs(DO_record record, short[] waveData)
        {
            this.Record = record;
            this.WaveDate = waveData;
        }
    }
}
