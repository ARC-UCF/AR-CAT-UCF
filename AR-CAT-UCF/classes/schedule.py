from collections.abc import Collection
from datetime import datetime, timedelta

class Schedule():
    def __init__(self, *, months=None, weekdays=None, days=None, hours=None, minutes=None, grace_period=None):
        self.months = months
        self.weekdays = weekdays
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.grace_period = grace_period
        
    def should_send(self, lastsent, now: datetime):
        if not self.matches(now):
            return False
        
        if lastsent is not None and self.is_same_occurrence(lastsent=lastsent, now=now):
            return False
        
        if self.grace_period is not None:
            window_start = now.replace(second=0, microsecond=0)
            if now > window_start + self.grace_period:
                return False
        
        return True
        
    def is_same_occurrence(self, lastsent: datetime | None, now: datetime):
        
        if lastsent is None:
            return False
        
        if self.minutes is not None:
            return (
                lastsent.year == now.year
                and lastsent.month == now.month
                and lastsent.day == now.day
                and lastsent.hour == now.hour
                and lastsent.minute == now.minute
            )
            
        if self.hours is not None:
            return (
                lastsent.year == now.year
                and lastsent.month == now.month
                and lastsent.day == now.day
                and lastsent.hour == now.hour
            )
            
        if self.days is not None:
            return (
                lastsent.year == now.year
                and lastsent.month == now.month
                and lastsent.day == now.day
            )
            
        if self.weekdays is not None:
            return (
                lastsent.isocalendar().year == now.isocalendar().year
                and lastsent.isocalendar().week == now.isocalendar().week
                and lastsent.isocalendar().weekday == now.isocalendar().weekday
            )
            
        if self.months is not None:
            return (
                lastsent.year == now.year
                and lastsent.month == now.month
            )
            
        return False
        
    @staticmethod
    def _matches(value, rule):
        if rule is None:
            return True
        
        if isinstance(rule, range):
            return value in rule
        
        if isinstance(rule, Collection) and not isinstance(rule, str):
            return value in rule
        
        return value == rule
    
    def matches(self, now):
        return (
            self._matches(now.month, self.months)
            and self._matches(now.weekday(), self.weekdays)
            and self._matches(now.day, self.days)
            and self._matches(now.hour, self.hours)
            and self._matches(now.minute, self.minutes)
        )
        
    def to_dict(self):
        return {
            "months": self.months,
            "weekdays": self.weekdays,
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes,
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(**data)