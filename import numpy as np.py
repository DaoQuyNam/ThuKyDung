import numpy as np
import talib
#c:\users\quyla\appdata\local\programs\python\python310\lib\site-packages (from TA-Lib==0.4.24) (1.26.4)
c = np.random.randn(100)
k, d = talib.STOCHRSI(c)
print(k)