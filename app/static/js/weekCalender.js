/**
 * Created by nicolas on 5/4/15.
 */
/*
	jQuery Document ready
*/
$(document).ready(function()
{
	/*
		store calendar dom into variable
	*/
	var $calendar = $('#calendar');
	var id = 10;

	$calendar.weekCalendar(
	{
		/*
			define slot between each hours,
			4 define 4 time slot,
			which indicate 15 minutes,
			2 define 2 times slot,
			which indicate 30 minutes,
			between each hours
		*/
		timeslotsPerHour : 4,
		/*
			[boolean | default: false]
			Whether the calendar will allow events to overlap.
			Events will be moved or resized if necessary
			if they are dragged or resized to a location
			that overlaps another calendar event.
		*/
		allowCalEventOverlap : true,
		/*
			[boolean | default: false]
			If true,
			events that overlap will be rendered separately without any overlap.
		*/
		overlapEventsSeparate: true,
		/*
			[integer | default: 0]
			Determines what day of the week to start on.
			0 = sunday, 1 = monday etc
		*/
		firstDayOfWeek : 1,
		/*
			[object | default:
			{start: 8, end: 18, limitDisplay: false}]
			An object that specifies which hours within the day to render as
		*/
		businessHours :{start: 0, end: 24, limitDisplay: true },
		/*
			[integer | default: 7]
			Determines how many days to show.
			Note that next/prev weekly navigation is still
			based on weeks rather than the number of days displaying
		*/
		daysToShow : 7,
		/*
			A function that can return a height in pixels for the calendar.
			If the height of the calendar is less than the space it takes to render it,
			the calendar will scroll within the timeslot
			region while the day column headers will remain fixed
		*/
		height : function($calendar)
		{
			return $(window).height() - $("h1").outerHeight() - 1;
		},
		/*
			Called prior to rendering an event.
			Allows modification of the eventElement
			or the ability to return a different element
		*/
		eventRender : function(calEvent, $event)
		{
			if (calEvent.end.getTime() < new Date().getTime())
			{
				$event.css("backgroundColor", "#aaa");
				$event.find(".wc-time").css({
					"backgroundColor" : "#999",
					"border" : "1px solid #888"
				});
			}
		},
		/*
			Called on each event to determine whether
			it should be draggable or not.
			Default function returns true on all events.
		*/
		draggable : function(calEvent, $event)
		{

			return calEvent.readOnly = false;
		},
		/*
			Called on each event to determine whether
			it should be resizable or not.
			Default function returns true on all events.
		*/
		resizable : function(calEvent, $event)
		{

			return calEvent.readOnly = false;
		},
		/*
			Called on creation of a new calendar event
		*/
		eventNew : function(calEvent, $event)
		{
			/*
				we are creating dialog box,
				which will be shown when event is selected.
			*/
			var $dialogContent = $("#event_edit_container");
			resetForm($dialogContent);
			var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
			var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
			var titleField = $dialogContent.find("input[name='title']");
			var bodyField = $dialogContent.find("textarea[name='body']");

			$dialogContent.dialog(
			{
				modal: true,
				title: "New Calendar Event",
				close: function()
				{
					$dialogContent.dialog("destroy");
					$dialogContent.hide();
					$('#calendar').weekCalendar("removeUnsavedEvents");
				},
				buttons:
				{
					save : function()
					{
						calEvent.id = id;
						id++;
						calEvent.start = new Date(startField.val());
						calEvent.end = new Date(endField.val());
						calEvent.title = titleField.val();
						calEvent.body = bodyField.val();

						$calendar.weekCalendar("removeUnsavedEvents");
						$calendar.weekCalendar("updateEvent", calEvent);
						$dialogContent.dialog("close");
					},
					cancel : function()
					{
						$dialogContent.dialog("close");
					}
				}
			}).show();

			$dialogContent.find(".date_holder").text($calendar.weekCalendar("formatDate", calEvent.start));
			setupStartAndEndTimeFields(startField, endField, calEvent, $calendar.weekCalendar("getTimeslotTimes", calEvent.start));
		},
		/*
			Called on click of a calendar event
		*/
		eventClick : function(calEvent, $event)
		{

			if (calEvent.readOnly)
			{
				return;
			}
			/*
				calling dialog box with events data filled in.
			*/
			var $dialogContent = $("#event_edit_container");
			resetForm($dialogContent);
			var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
			var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
			var titleField = $dialogContent.find("input[name='title']").val(calEvent.title);
			var bodyField = $dialogContent.find("textarea[name='body']");
			bodyField.val(calEvent.body);

			$dialogContent.dialog(
			{
				modal: true,
				title: "Edit - " + calEvent.title,
				close: function()
				{
					$dialogContent.dialog("destroy");
					$dialogContent.hide();
					$('#calendar').weekCalendar("removeUnsavedEvents");
				},
				buttons:
				{
					save : function()
					{
						calEvent.start = new Date(startField.val());
						calEvent.end = new Date(endField.val());
						calEvent.title = titleField.val();
						calEvent.body = bodyField.val();

						$calendar.weekCalendar("updateEvent", calEvent);
						$dialogContent.dialog("close");
					},
					"delete" : function()
					{
						$calendar.weekCalendar("removeEvent", calEvent.id);
						$dialogContent.dialog("close");
					},
					cancel : function()
					{
						$dialogContent.dialog("close");
					}
				}
			}).show();

			var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
			var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
			$dialogContent.find(".date_holder").text($calendar.weekCalendar("formatDate", calEvent.start));
			setupStartAndEndTimeFields(startField, endField, calEvent, $calendar.weekCalendar("getTimeslotTimes", calEvent.start));
			$(window).resize().resize(); //fixes a bug in modal overlay size ??
		}
	});

	function resetForm($dialogContent)
	{
		$dialogContent.find("input").val("");
		$dialogContent.find("textarea").val("");
	}

	/*
		* Sets up the start and end time fields in the calendar event
		* form for editing based on the calendar event being edited
    */
	function setupStartAndEndTimeFields($startTimeField, $endTimeField, calEvent, timeslotTimes)
	{

		for (var i = 0; i < timeslotTimes.length; i++)
		{
			var startTime = timeslotTimes[i].start;
			var endTime = timeslotTimes[i].end;
			var startSelected = "";
			if (startTime.getTime() === calEvent.start.getTime())
			{
				startSelected = "selected=\"selected\"";
			}
			var endSelected = "";
			if (endTime.getTime() === calEvent.end.getTime())
			{
				endSelected = "selected=\"selected\"";
			}

			$startTimeField.append("<option value=\"" + startTime + "\" " + startSelected + ">" + timeslotTimes[i].startFormatted + "</option>");
			$endTimeField.append("<option value=\"" + endTime + "\" " + endSelected + ">" + timeslotTimes[i].endFormatted + "</option>");
		}
		$endTimeOptions = $endTimeField.find("option");
		$startTimeField.trigger("change");
	}
});