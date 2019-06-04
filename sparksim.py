from fractions import Fraction

class App:
    def __init__(self, id, duration, deadline):
        self.id = id
        self.duration = duration
        self.nominalRate = Fraction(1, duration)
        self.deadline = deadline
    def __repr__(self):
        return "app" + str(self.id)
    def __hash__(self):
        return self.id
    def __eq__(self, other):
        return self.id == other.id

class Scheduler:
    def addProgress(self, apps):
        raise Exception("Not Implemented")

class Spark:
    def __init__(self, scheduler, running={}, ended={}):
        self.running = dict(running)
        self.ended = dict(ended)
        self.scheduler = scheduler

    def schedule(self, app, time):
        if app in self.running:
            return self
        elif app in self.ended:
            return self

        all = list(self.running.keys()) + list(self.ended.keys())
        for a in all:
            if a.id == app.id -1:
                break
        else:
            return self

        running = dict(self.running)
        running[app] = (time, Fraction())
        return Spark(self.scheduler, running, self.ended)

    def tick(self, time):
        if not self.running:
            return self

        running = dict(self.running)
        ended = dict(self.ended)

        self.scheduler.addProgress(running, time)

        for app, value in running.items():
            if value[1] >= 1:
                ended[app] = (value[0], time)
        for app in ended:
            if app in running:
                del running[app]

        return Spark(self.scheduler, running, ended)

    def __eq__(self, other):
        return self.running == other.running\
                and self.ended == other.ended

    def __hash__(self):
        return self.__repr__().__hash__()

    def hasViolations(self, apps, steps):
        for app in apps:
            if app not in self.ended:
                return True
            elif app in self.ended and self.ended[app][1] - self.ended[app][0] > app.deadline:
                return True
        return False

    def computeViolations(self, apps, steps):
        for app in apps:
            if app in self.ended and self.ended[app][1] - self.ended[app][0] > app.deadline:
                return True
        return False

    def computeScenarioViolations(self, apps, steps):
        if self.computeViolations(apps, steps) or self.computeUnfisibility(apps, steps):
            return False
        for app in apps:
            if app not in self.ended and app in self.running and self.running[app][0]+app.duration <= steps:
                return True
        return False

    def computeUnfisibility(self, apps, steps):
        if self.computeViolations(apps, steps):
            return False
        for app in apps:
            if app not in self.ended and app not in self.running:
                return True
            if app not in self.ended and app in self.running and self.running[app][0]+app.duration > steps:
                return True
        return False

    def computeNonViolations(self, apps, steps):
        return not self.computeViolations(apps, steps) \
                and not self.computeScenarioViolations(apps, steps) \
                and not self.computeUnfisibility(apps, steps)

    def __repr__(self):
        return "r:%s, e:%s\n" % (self.running, self.ended)

    def error(self, apps):
        eA = eD = 0.0
        for app, value in self.ended.items():
            e = float(app.deadline - (self.ended[app][1] - self.ended[app][0])) / float(app.deadline)
            if e < 0:
                eD += abs(e)
            else:
                eA += e
        return eA/len(apps), eD/len(apps)


def nextStates(apps, state, time):
    if not apps:
        return {state}
    app = apps[0]
    if not state.running:
        return nextStates(apps[1:], state.schedule(app, time), time)
    else:
        return nextStates(apps[1:], state.schedule(app, time), time) | nextStates(apps[1:], state, time)


def simulate(initial, apps, steps):
    print(initial.scheduler.__class__.__name__, "-", steps)
    states = {initial}
    for t in range(0, steps+1, 1):
        newStates = set()
        for state in states:
             newStates |= nextStates(apps,state.tick(t), t)
        #print(t, len(newStates))
        states = newStates


    eA = sum(map(lambda s: s.error(apps)[0], states))/len(states)
    eD = sum(map(lambda s: s.error(apps)[1], states))/len(states)
    print("eA = %.1f%%\neD = %.9f%%" % (eA*100, eD*100))

    violations = len([s for s in states if s.computeViolations(apps, steps)])/len(states)*100
    scenarioViolations = len([s for s in states if s.computeScenarioViolations(apps, steps)])/len(states)*100
    unfisibles = len([s for s in states if s.computeUnfisibility(apps, steps)])/len(states)*100
    nonViolations = len([s for s in states if s.computeNonViolations(apps, steps)])/len(states)*100
    print("Violations = %.1f%%\nScenario Violations = %.1f%%\nUnfisibles = %.1f%%\nNon Violations = %.1f%%" \
            % (violations, scenarioViolations, unfisibles, nonViolations))
