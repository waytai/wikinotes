from django.db import models
from django.contrib.auth.models import User
from wiki.models.history import HistoryItem

class Course(models.Model):
	class Meta:
		app_label = 'wiki'

	department = models.ForeignKey('Department')
	number = models.IntegerField()
	name = models.CharField(max_length=255)
	description = models.CharField(max_length=255) # change this later
	credits = models.IntegerField() # Note - what if it's a float etc
	watchers = models.ManyToManyField(User)

	def __unicode__(self):
		return "%s %d" % (self.department.short_name, self.number)

	def url(self):
		return '/%s_%d' % (self.department.short_name, self.number)

	def num_watchers(self):
		return len(self.watchers.all())

	def num_pages(self):
		count = 0
		course_sems = self.coursesemester_set.all()
		for sem in course_sems:
			num_pages = sem.page_set.count()
			count += num_pages
		return count

	"""
		NOTE: The following methods are temporary methods. They should really be instance methods on the user, not on the course. But that will have to wait until I figure out the best way to easily extend the user model while still having access to it through request.user
	"""
	def has_watcher(self, user):
		return (user in self.watchers.all())

	def add_watcher(self, user):
		self.watchers.add(user)
		# Add the history item, find a better way to do this later
		history_item = HistoryItem(user=user, action='started watching', course=self)
		history_item.save()

	def remove_watcher(self, user):
		self.watchers.remove(user)
		history_item = HistoryItem(user=user, action='stopped watching', course=self)
		history_item.save()

class CourseSemester(models.Model):
	class Meta:
		app_label = 'wiki'
		unique_together = ('term', 'year', 'course')

	course = models.ForeignKey('Course')
	grading_scheme = models.CharField(max_length=255, null=True)
	professors = models.ManyToManyField('Professor', null=True)
	schedule = models.CharField(max_length=100, null=True)
	midterm_info = models.CharField(max_length=255, null=True)
	final_info = models.CharField(max_length=255, null=True)
	term = models.CharField(max_length=6) # Winter/Summer etc
	year = models.IntegerField(max_length=4) # Because ... yeah

	def __unicode__(self):
		return "%s (%s %d)" % (self.course, self.term.title(), self.year)

	def get_semester(self):
		# For printing out. Returns Term year
		return "%s %d" % (self.term.title(), self.year)

class Professor(models.Model):
	class Meta:
		app_label = 'wiki'

	name = models.CharField(max_length=100)
