if (window.jQuery) {
    $(document).ready(function() {

        function calSuccess(data, textStatus, jqXHR) {
            $('#event-calendar').html(data.calendar);
            if ($('#month-and-year').length)
                $('#month-and-year').html(data.month_and_year);
            pop_();
        }

        function eventListSuccess(data, textStatus, jqXHR) {
            var bg
            , fnt
            , events = data.events
            , l = $('.calendar-list')
            ;

            l.html('');

            for (day in events) {
                for (ev in events[day]) {
                    var e = events[day][ev];

                    bg = '#' + e.fields.background_color_custom;
                    if (bg === '#')
                        bg = '#' + e.fields.background_color;

                    fnt = '#' + e.fields.font_color_custom;
                    if (fnt === '#')
                        fnt = '#' + e.fields.font_color;

                    l.append(
                    '<li class="month-event" '
                    + ' style="background:' + bg + '; color:' + fnt + ';">'
                    + '<div class="date-widget">'
                    + '<div class="widget-month">'
                    + data.month + '</div>'
                    + '<div class="widget-day">'
                    + day + '</div>'
                    + '<div class="widget-year">'
                    + e.weekday  + '</div>'
                    + '</div>'
                    + '<div class="month-event-title">'
                    + '<a href="/calendar/event/' + e.pk 
                    + '" style="color:' + fnt + ';">'
                    + e.fields.title + '</a></div></li>'
                    );
                }
            }
        }

        function daySuccess(data, textStatus, jqXHR) {
            var l = $('.day-event-list');
            l.html('');
            data.events.forEach(function(e) {
                l.append(
                    '<li><a href="/calendar/event/' + e.pk + '">'
                    + e.fields.title + '</a></li>'
                    )
            });

            if (l.html() === "")
                l.append('<li>Oops.. No events!</li>');

            $('#cal-day-prev').attr('href','?cal_prev=' + data.prev);
            $('#cal-day-next').attr('href','?cal_next=' + data.nxt);
            $('#cal-day-year').html(data.year);
            $('#cal-day-month').html(data.month);
            $('#cal-day-day').html(data.day);
        }

        function pop_() {
            // popover requires twitter bootstrap w/ tooltip plugin
            if (typeof $().popover == 'function') {
                $(document).on('click', '.event-anch', function(event) {
                    event.preventDefault();
                });
                $('.calendar-event').popover({trigger:'click', html:true});
            }
        }

        // event listener for day view's next/prev
        $(document).on('click', '.cal-day', function(event) {
            event.preventDefault();
            var qs = ''
            , cat = $('#cal-day-category').html()
            , tag = $('#cal-day-tag').html()
            ;

            if (cat !== undefined)
                qs += '&cal_category=' + cat;
            if (tag !== undefined)
                qs += '&cal_tag=' + tag;
        
            $.ajax({ 
                type: "GET",
                url: this.href + qs,
                data: {},
                success: daySuccess,
                dataType: 'json'
            });
        });
        
        pop_();

        ['#cal-today-btn', '.month-arrow-left', '.month-arrow-right']
        .forEach(function (el) {
            $(document).on('click', el, function(event) {
                var qs = '?'
                , data = {}
                , list = $('#event-list')
                , cal = $('#event-calendar')
                ;

                event.preventDefault();

                $('.popover').remove();  // remove any open popovers

                // if mini calendar, make sure we get right calendar back
                // by passing cal_mini=True qs
                if (cal.hasClass('calendar-mini'))
                    qs += 'cal_mini=true&';

                if (el !== '#cal-today-btn') {
                    // get cal_prev or cal_next querystring
                    qs += $(el + " > a").attr('href').slice(1);
                    // if cal_ignore qs present, don't bother adding date qs
                    if ($.inArray("cal_ignore=true", qs.split("&")) === -1) {
                        // try to get year & month from url
                        var loc = window.location.pathname.split('/');
                        if (loc.length == 5 && loc[1] == 'calendar') {
                            data.cal_year = loc[2];
                            data.cal_month = loc[3];
                        }
                    }
                } else {
                    var t = $('.month-arrow-left > a')
                        .attr('href').slice(1).split('&');

                    for (var i = 0; i < t.length; i++) {
                        var name = t[i].split('=')[0];
                        if (name === 'cal_category' || name === 'cal_tag')
                           qs += t[i] + '&'; 
                    }

                    // When the 'Today' button is pressed, we want to start
                    // from today, which means ignoring any dates given in the
                    // url or via querystrings. 
                    // That's what cal_ignore qs is for.
                    qs += 'cal_ignore=true';

                    if ($('#month-list-events-title').length)
                        $('#month-list-events-title').html("Events");
                }

                /* Request the month's calendar and/or event-list via ajax */
                if (cal.length && list.length) {
                    $.getJSON('/calendar/cal-and-list/shift/' + qs, data,
                            [calSuccess, eventListSuccess]);
                } else if (cal.length) {
                    $.getJSON('/calendar/month/shift/' + qs, data, calSuccess);
                } else if (list.length) {
                    $.getJSON('/calendar/event-list/shift/' + qs, data, 
                            eventListSuccess);
                }
            });
        });
    });
}
