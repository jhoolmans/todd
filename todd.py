#!/usr/bin/env python
import sys

if sys.version_info < (3, 6):
    sys.exit('Python < 3.6 is not supported')

from todd.main import main
main()
