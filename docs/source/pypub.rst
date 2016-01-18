Bithex
**********

Bithex is a Python 2 library to analyze bitcoin scripts.

****************
Installation
****************
The current release of bithex is available through pip:

    $ pip install bithex

**************
Quickstart
**************

>>> from bithex import compile_hex
>>> compile_hex('aa206fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d619000000000087')
'OP_HASH256 6fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000 OP_EQUAL'

*************************
Copyright and License
*************************

Copyright (c) 2015 William Cember

Licensed under the MIT License

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.