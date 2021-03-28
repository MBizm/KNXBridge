# -*- coding: utf-8 -*-

""" See (in french):

 - http://gillesfabio.com/blog/2010/12/16/python-et-les-decorateurs
 - http://www.gawel.org/howtos/python-decorators
 """


class Scheduler(object):
    """
    """
    def __init__(self):
        """
        """
        super(Scheduler, self).__init__()

        print "Scheduler.__init__()"

        self._funcs = []

    def every(self, hours=None, minutes=None, seconds=None):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "Scheduler.every(hours=%s, minutes=%s, seconds=%s)" % (hours, minutes, seconds)
        return decorated

    def at(self):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "Scheduler.at()"
        return decorated

    def after(self, hours=None, minutes=None, seconds=None):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "Scheduler.after(hours=%s, minutes=%s, seconds=%s)" % (hours, minutes, seconds)
        return decorated

    def cron(self):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "Scheduler.cron()"
        return decorated


class Group(object):
    """
    """
    def __init__(self):
        """
        """
        super(Group, self).__init__()

        print "Group.__init__()"

        self._funcs = []

    def __call__(self, ga=None, id=None):
        """
        """
        print "Group.__call__(ga=%s, id=%s)" % (ga, id)
        return self

    def find(self, ga=None, id_=None):
        """
        """
        print "Group.find(ga=%s, id_=%s)" % (ga, id)

    def changed(self, from_=None, to=None):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "Group.changed(from_=%s, to=%s)" % (from_, to)
        return decorated


class System(object):
    """
    """
    def __init__(self):
        """
        """
        super(System, self).__init__()

        print "System.__init__()"

        self._funcs = []

    def start(self):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "System.start()"
        return decorated

    def stop(self):
        """ Decorator
        """
        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._funcs.append(func)
            return func

        print "System.stop()"
        return decorated


class Trigger(object):
    """
    """
    def __init__(self):
        """
        """
        super(Trigger, self).__init__()

        print "Trigger.__init__()"

        self.schedule = Scheduler()
        self.group = Group()
        self.system = System()


trigger = Trigger()

myTrig = trigger.group(ga="1/1/1").changed()

@trigger.schedule.every(minutes=1)
@eval("trigger.group(ga='1/1/1').changed()")
#@myTrig
@trigger.system.start()
def heatingBathroomManagement(event):
    """
    """
    print "heatingBathroomManagement(): event=%s" % event


class Test(object):

    @trigger.schedule.every(minutes=1)
    def test(self):
        print "test"

t = Test()
print t.test.im_func


print "Scheduler funcs=%s" % trigger.schedule._funcs
print "Group funcs=%s" % trigger.group._funcs
print "System funcs=%s" % trigger.system._funcs
