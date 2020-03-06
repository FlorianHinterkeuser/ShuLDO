#
# Testplot mit Grafik-Speicherung als png und eps
#
# https://apmonitor.com/che263/index.php/Main/PythonPlots
#
#
#
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0,7,1000)         # (linkes limit, rechtes limit, Anzahl Stuetzstellen)
y = np.sin(x)
z = np.cos(x)

plt.plot(x,y,'b--',linewidth=3)     # r-- gibt (rote) gestrichelte linie
plt.plot(x,z,'g:',linewidth=2)      # k:  gibt (schwarze) gepunktete linie
plt.legend(['y','z'])
plt.xlabel('x')
plt.ylabel('function values')
plt.xlim([0, 2*np.pi])
plt.ylim([-1.1, 1.1])
plt.savefig('myFigure.pdf')
#plt.savefig('myFigure.eps')
plt.show()