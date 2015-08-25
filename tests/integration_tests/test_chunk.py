from __future__ import unicode_literals

from calendar import monthrange

from django.core.urlresolvers import reverse

from .event_factory import create_event, SetMeUp


class ChunkEventListViewTest(SetMeUp):
    """
    Test 'chunk' events, which are events that start and end on different
    days, thereby forming a 'chunk' of days during which the event lasts.
    """

    def check_dates(self, event, valid_dates):
        """A DRY helper function"""
        for month, days in valid_dates.items():
            response = self.client.get(reverse(
                'calendar:list', kwargs={'year': '2014', 'month': month}
            ))
            self.clean_whitespace(response)
            self.assertContains(response, event.title)

            for day in days:
                self.assertContains(response, self.cal_str(day))

            [self.assertNotContains(response, self.cal_str(day)) for
             day in range(1, monthrange(2014, int(month))[1] + 1)
             if day not in days]

    def test_list_view_with_chunk_starts_and_ends_same_month(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 5),
            created_by=self.user,
            title="Lily",
            description="'chunk' event that lasts 5 days and doesn't repeat.",
        )
        valid_dates = {'03': [1, 2, 3, 4, 5]}
        self.check_dates(event, valid_dates)

    def test_list_view_with_chunk_starts_ends_different_month(self):
        event = create_event(
            start_date=(2014, 3, 28),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Sammy",
            description="'chunk' event that lasts 5 days and doesn't repeat.",
        )

        valid_dates = {'03': [28, 29, 30, 31], '04': [1, 2]}
        self.check_dates(event, valid_dates)

    def test_list_view_with_chunk_starts_ends_different_month2(self):
        """
        This tests that the issue opened on github by
        Joe Tennies (github.com/Rotund) has been resolved
        thanks to the work of Yaroslav Klyuyev (github.com/imposeren)
        """
        event = create_event(
            start_date=(2014, 7, 31),
            end_date=(2014, 8, 1),
            created_by=self.user,
            title="Cool",
            description="'chunk' event that lasts 2 days and doesn't repeat.",
        )

        valid_dates = {'07': [31], '08': [1]}
        self.check_dates(event, valid_dates)
