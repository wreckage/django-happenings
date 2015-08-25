from __future__ import unicode_literals

from datetime import timedelta, date

from django.core.exceptions import ValidationError
from django.utils import timezone

from ..integration_tests.event_factory import create_event, SetMeUp
from happenings.models import Event, Location, Category, Tag


# Note that whenever the create_event() factory method is used, it
# creates an event and calls event.full_clean() and event.save() if the full
# option is not given as False, so we don't need to call them again when
# testing for validation built in to those functions
class EventModelTest(SetMeUp):
    def test_start_date_before_end_date(self):
        """
        Creating an event with an end_date before its start_date should
        raise a validation error. Notice that full_clean must manually be
        called, b/c it isn't called automatically when creating an object
        this way (It is called in the admin, however).
        """
        with self.assertRaises(ValidationError):
            create_event(
                start_date=(2015, 2, 15),
                end_date=(2015, 2, 12),
                created_by=self.user,
                title="The Event",
                description="This is an event for next month."
            )

    def test_out_of_range_chunk(self):
        """
        The difference between start_date and end_date for an
        event should be no more than 7 days.
        """
        # we should get a ValidationError here...
        with self.assertRaises(ValidationError):
            event = Event.objects.create(
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=8),
                all_day=True,
                created_by=self.user,
                title="The big event",
                description="Amazing event",
                repeat="NEVER",
            )
            self.assertEqual(event.get_start_end_diff(), 8)
            event.full_clean()

        # ...but not here
        event = create_event(
            start_date=(2015, 3, 15),
            end_date=(2015, 3, 22),
            created_by=self.user,
            title="The Other Event",
            description="Awesome event"
        )
        self.assertEqual(event.get_start_end_diff(), 7)

    def test_end_repeat_date_but_no_repeat(self):
        """
        Creating an event with an end_repeat date but that's not supposed to
        repeat (i.e. repeat is set to 'NEVER') should raise a ValidationError.
        """
        event = Event.objects.create(
            start_date=timezone.now(),
            end_date=timezone.now(),
            all_day=True,
            created_by=self.user,
            title="The big event",
            description="Amazing event",
            repeat="NEVER",
            end_repeat=(timezone.now() + timedelta(days=14))
        )
        event.full_clean()
        self.assertEqual(event.end_repeat, None)

    def test_err_chunk_repeat_weekday_daily(self):
        """
        Events that start and end on different days shouldn't
        be allowed to repeat every day or every weekday.
        """
        with self.assertRaises(ValidationError):
            create_event(
                start_date=(2015, 2, 15),
                end_date=(2015, 2, 16),
                created_by=self.user,
                title="The Main Event",
                description="super event",
                repeat="DAILY"
            )

        with self.assertRaises(ValidationError):
            create_event(
                start_date=(2015, 2, 15),
                end_date=(2015, 2, 16),
                created_by=self.user,
                title="The Other Main Event",
                description="super duper event",
                repeat="WEEKDAY"
            )

# XXX slugs have been removed
#    def test_invalid_title(self):
#        """
#        Test that titles like '???', that create a blank string
#        when slugified, use either their pk (if they have one)
#        or 0 for their slug.
#        """
#        event1 = Event.objects.create(
#            start_date=timezone.now(),
#            end_date=timezone.now() + timedelta(days=2),
#            all_day=True,
#            created_by=self.user,
#            title="???",
#            description="Amazing event",
#            repeat="NEVER",
#        )
#        event2 = Event.objects.create(
#            start_date=timezone.now() + timedelta(days=3),
#            end_date=timezone.now() + timedelta(days=5),
#            all_day=True,
#            created_by=self.user,
#            title="???",
#            description="Amazing event",
#            repeat="NEVER",
#        )
#        event3 = create_event(
#            start_date=(2013, 3, 14),
#            end_date=(2013, 3, 14),
#            created_by=self.user,
#            title="???",
#            description="Event!",
#        )
#        event4 = Event.objects.create(
#            start_date=timezone.now() + timedelta(days=7),
#            end_date=timezone.now() + timedelta(days=8),
#            all_day=True,
#            created_by=self.user,
#            title="???",
#            description="Amazing event",
#            repeat="NEVER",
#        )
#        event1.full_clean()
#        event2.full_clean()
#        event4.full_clean()
#        # events 1 and 2 didn't have a pk when they were saved, so their slugs
#        # starts from 0. Event 3 did have a pk, so it gets used in the slug.
#        self.assertEqual(event1.slug, "0")
#        self.assertEqual(event2.slug, "0-2")
#        self.assertEqual(event4.slug, "0-3")
#        self.assertEqual(event3.slug, str(event3.pk))


class EventColorTest(SetMeUp):
    def test_valid_color_injection(self):
        Event.COLORS += [('ff00ff', 'fuchsia')]
        event = Event.objects.create(
            start_date=timezone.now(),
            end_date=timezone.now(),
            all_day=True,
            created_by=self.user,
            title="The big event",
            description="Amazing event",
            repeat="NEVER",
            background_color="ff00ff",
        )
        event.full_clean()
        self.assertEqual('ff00ff', event.background_color)

    def test_invalid_color_injection(self):
        with self.assertRaises(ValidationError) as ve:
            Event.COLORS += [('ff00', 'fuchsia')]
            event = Event.objects.create(
                start_date=timezone.now(),
                end_date=timezone.now(),
                all_day=True,
                created_by=self.user,
                title="The big event",
                description="Amazing event",
                repeat="NEVER",
                background_color="ff00",
            )
            event.full_clean()
        self.assertEqual(
            ve.exception.messages[0], 'Color must be a valid hex triplet.'
        )

    def test_invalid_custom_color(self):
        with self.assertRaises(ValidationError) as ve:
            event = Event.objects.create(
                start_date=timezone.now(),
                end_date=timezone.now(),
                all_day=True,
                created_by=self.user,
                title="The big event",
                description="Amazing event",
                repeat="NEVER",
                font_color_custom="ff00zz",
            )
            event.full_clean()
        self.assertEqual(
            ve.exception.messages[0], 'Color must be a valid hex triplet.'
        )


class ModelMethodsTest(SetMeUp):
    def test_event_str(self):
        event = create_event(
            created_by=self.user,
            title="The Event",
            description="This is an event."
        )
        self.assertEqual(event.__str__(), event.title)

    def test_location_str(self):
        location = Location.objects.create(name="The Living End")
        self.assertEqual(location.__str__(), location.name)

    def test_category_str(self):
        cat = Category.objects.create(title="birthdays")
        self.assertEqual(cat.__str__(), cat.title)

    def test_tag_str(self):
        tag = Tag.objects.create(name="birthday")
        self.assertEqual(tag.__str__(), tag.name)

    def test_cancellation_str(self):
        event = create_event(
            created_by=self.user,
            title="The Event",
            description="This is an event."
        )
        c = event.cancellations.create(
            reason="Out of town",
            date=date(2014, 5, 30)
        )
        self.assertEqual(c.__str__(),
                         event.title + ' - ' + c.date.strftime('%Y-%m-%d'))

    def test_start_end_diff(self):
        """
        Test that we get the correct difference between days when an
        event starts in December and ends in January.
        """
        event = create_event(
            start_date=(2013, 12, 31),
            end_date=(2014, 1, 1),
            created_by=self.user,
            title="The Event",
            description="Special event"
        )
        self.assertEqual(1, event.get_start_end_diff())
