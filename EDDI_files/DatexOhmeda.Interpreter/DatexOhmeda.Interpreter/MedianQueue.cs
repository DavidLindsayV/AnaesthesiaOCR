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
    public class MedianQueue<T>
    {
        public MedianQueue(int size)
        {
            if (size % 2 == 0)
                throw new ArgumentOutOfRangeException("size", "must be an odd number");

            this._size = size;
            _medianPosition = (size - 1) / 2;
            _queue = new Queue<T>(size);
            Reset();
        }

        public void Reset()
        {
            _queue.Clear();
        }

        public void Enqueue(T value)
        {
            if (Count == _size)
                _queue.Dequeue();

            _queue.Enqueue(value);

            if (Count == _size)
            {
                // calculate
                T[] data = _queue.ToArray();
                Array.Sort(data);

                Median = data[_medianPosition];
            }
        }
        
        public T Median { get; private set; }

        public int Count { get { return _queue.Count; } }

        private int _size;
        private int _medianPosition = 0;
        private Queue<T> _queue;
    }
}
