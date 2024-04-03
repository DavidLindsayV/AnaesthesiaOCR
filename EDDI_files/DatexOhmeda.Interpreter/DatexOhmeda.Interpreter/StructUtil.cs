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
    public static class StructUtil
    {
        public static unsafe T ReadStruct<T>(byte* in_pbuf, int in_offset)
        {
            byte* pStruct = in_pbuf + in_offset;
            IntPtr ptr = new IntPtr(pStruct);
            T res = (T)Marshal.PtrToStructure(ptr, typeof(T));
            return res;
        }

        public static unsafe T ReadStruct<T>(byte[] in_buf, int in_offset)
        {
            fixed (byte* pBuf = in_buf)
            {
                return ReadStruct<T>(pBuf, in_offset);
            }
        }

        public static unsafe void ReadShortArray(byte* in_pbuf, int in_offset, ref short[] ref_array, int in_arrayIndex, int in_count)
        {
            IntPtr ptr = new IntPtr(in_pbuf);
            for (int n = 0; n < in_count; n++)
                ref_array[n + in_arrayIndex] = Marshal.ReadInt16(ptr, in_offset + n * sizeof(short));
        }

        public static unsafe void ReadShortArray(byte* in_pbuf, int in_offset, ref short[] ref_array)
        {
            ReadShortArray(in_pbuf, in_offset, ref ref_array, 0, ref_array.Length);
        }

        public static unsafe void WriteStruct<T>(T in_struct, byte* ref_pbuf, int in_offset)
        {
            byte* pStruct = ref_pbuf + in_offset;
            IntPtr ptr = new IntPtr(pStruct);
            Marshal.StructureToPtr(in_struct, ptr, false);
        }

        public static unsafe void WriteStruct<T>(T in_struct, ref byte[] ref_buf, int in_offset)
        {
            fixed (byte* pBuf = ref_buf)
            {
                WriteStruct<T>(in_struct, pBuf, in_offset);
            }
        }
    }
}
