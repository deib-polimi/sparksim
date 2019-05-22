from sparksim import Scheduler
from fractions import Fraction

class FIFO(Scheduler):
    def addProgress(self, runningApps, time):
        t = a = None
        for app, value in runningApps.items():
            if not t or value[0] < t[0]:
                t = value
                a = app
        runningApps[a] = (t[0], t[1] + a.nominalRate)

class EDFAll(Scheduler):
    def addProgress(self, runningApps, time):
        r = t = a = None
        for app, value in runningApps.items():
            if not r or app.deadline-(time-value[0]) < r:
                r = app.deadline-(time-value[0])
                t = value
                a = app
        runningApps[a] = (t[0], t[1] + a.nominalRate)

class Fair(Scheduler):
    def addProgress(self, runningApps, time):
        p = Fraction(1, len(runningApps))
        for app, value in runningApps.items():
            runningApps[app] = (value[0], value[1] + p*app.nominalRate)

class EDFPure(Scheduler):
    def addProgress(self, runningApps, time):
        p = Fraction(1, 1)
        sitems = sorted(runningApps.items(), key=lambda i: i[0].deadline-(time-i[1][0]))
        for app, value in sitems:
            runningTime = time-value[0]
            remainingTime = app.deadline-runningTime
            if remainingTime <= 0:
                request = Fraction(p, 1)
            else:
                request = Fraction(Fraction(1-value[1], remainingTime), app.nominalRate)
            allocation = min(p, request)
            p -= allocation
            runningApps[app] = (value[0], value[1] + allocation*app.nominalRate)
            if p <= 0:
                break
