<template>
  <div
    class="h-full calendar-container"
    :class="{ 'modal-is-open': modalOpen }"
  >
    <FullCalendar ref="calendar" :options="calendarOptions" class="h-full" />
  </div>
</template>

<script setup>
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import timeGridPlugin from '@fullcalendar/timegrid'
import FullCalendar from '@fullcalendar/vue3'
import { computed, ref, watch } from 'vue'

const props = defineProps({
  tasks: {
    type: Object,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({}),
  },
  modalOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['eventClick', 'dateClick', 'eventDrop'])

const calendar = ref(null)

// Transform tasks data into calendar events
const calendarEvents = computed(() => {
  if (!props.tasks?.data?.data) return []

  const events = []
  const taskData = props.tasks.data.data

  // Handle both regular list view and kanban view data structures
  const tasks = Array.isArray(taskData)
    ? taskData
    : taskData.flatMap((column) => column.data || [])

  tasks.forEach((task) => {
    if (task.due_date) {
      events.push({
        id: task.name,
        title: task.title || 'Untitled Task',
        start: task.due_date,
        allDay: true,
        extendedProps: {
          status: task.status,
          priority: task.priority,
          assigned_to: task.assigned_to,
          description: task.description,
          reference_doctype: task.reference_doctype,
          reference_docname: task.reference_docname,
        },
        backgroundColor: getEventColor(task.status, task.priority),
        borderColor: getEventBorderColor(task.status, task.priority),
        textColor: getEventTextColor(task.status, task.priority),
      })
    }
  })

  return events
})

// Color coding based on task status and priority
function getEventColor(status, priority) {
  const statusColors = {
    Backlog: '#6b7280',
    Todo: '#3b82f6',
    'In Progress': '#f59e0b',
    Done: '#10b981',
    Cancelled: '#ef4444',
  }

  return statusColors[status] || '#6b7280'
}

function getEventBorderColor(status, priority) {
  const priorityBorders = {
    Low: '#d1d5db',
    Medium: '#f59e0b',
    High: '#ef4444',
    Urgent: '#dc2626',
  }

  return priorityBorders[priority] || '#d1d5db'
}

function getEventTextColor(status, priority) {
  return '#ffffff'
}

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  events: calendarEvents.value,
  editable: true,
  droppable: true,
  eventClick: handleEventClick,
  dateClick: handleDateClick,
  eventDrop: handleEventDrop,
  height: '100%',
  aspectRatio: 1.8,
  eventDisplay: 'block',
  dayMaxEvents: 3,
  moreLinkClick: 'popover',
  eventMouseEnter: handleEventMouseEnter,
  eventMouseLeave: handleEventMouseLeave,
  // Add specific z-index configuration
  zIndex: 1,
  ...props.options,
}))

function handleEventClick(info) {
  emit('eventClick', {
    task: info.event,
    taskId: info.event.id,
    extendedProps: info.event.extendedProps,
  })
}

function handleDateClick(info) {
  emit('dateClick', {
    date: info.date,
    dateStr: info.dateStr,
  })
}

function handleEventDrop(info) {
  emit('eventDrop', {
    task: info.event,
    oldStart: info.oldEvent.start,
    newStart: info.event.start,
    taskId: info.event.id,
  })
}

function handleEventMouseEnter(info) {
  // Add tooltip or hover effects if needed
  info.el.style.cursor = 'pointer'
}

function handleEventMouseLeave(info) {
  info.el.style.cursor = 'default'
}

// Watch for tasks changes and update calendar
watch(
  () => props.tasks,
  () => {
    if (calendar.value) {
      calendar.value.getApi().refetchEvents()
    }
  },
  { deep: true },
)

// Expose calendar API methods
defineExpose({
  getCalendarApi: () => calendar.value?.getApi(),
  refetchEvents: () => calendar.value?.getApi().refetchEvents(),
})
</script>

<style>
/* Global styles to fix z-index issues - using unscoped style */
.fc {
  z-index: 1 !important;
  isolation: isolate;
}

.fc * {
  z-index: 1 !important;
}

.fc-event,
.fc-daygrid-event,
.fc-timegrid-event {
  z-index: 1 !important;
}

.fc-popover {
  z-index: 10 !important;
}
</style>

<style scoped>
.calendar-container {
  position: relative;
  z-index: 1;
  isolation: isolate;
}

.calendar-container.modal-is-open {
  z-index: 0 !important;
  isolation: isolate;
}

.calendar-container.modal-is-open * {
  z-index: 0 !important;
}

.h-full {
  position: relative;
  z-index: 1;
}

:deep(.fc) {
  font-family: inherit;
  position: relative;
  z-index: 1 !important;
  isolation: isolate;
}

/* Force all FullCalendar elements to have low z-index */
:deep(.fc *) {
  z-index: 1 !important;
}

:deep(.fc-toolbar-title) {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
}

:deep(.fc-button) {
  background-color: #f3f4f6;
  border-color: #d1d5db;
  color: #374151;
  font-weight: 500;
}

:deep(.fc-button:hover) {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}

:deep(.fc-button-primary:not(:disabled):active),
:deep(.fc-button-primary:not(:disabled).fc-button-active) {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: #ffffff;
}

:deep(.fc-day-today) {
  background-color: #fef3c7 !important;
}

:deep(.fc-event) {
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 1 !important;
}

:deep(.fc-event-title) {
  font-weight: 500;
}

:deep(.fc-daygrid-event) {
  margin: 1px 2px;
  z-index: 1 !important;
}

:deep(.fc-more-link) {
  color: #3b82f6;
  font-weight: 500;
}

/* Ensure FullCalendar popovers don't interfere with modals */
:deep(.fc-popover) {
  z-index: 10 !important;
}

/* Force specific calendar elements to low z-index */
:deep(.fc-view-harness),
:deep(.fc-view),
:deep(.fc-daygrid),
:deep(.fc-timegrid),
:deep(.fc-daygrid-body),
:deep(.fc-timegrid-body),
:deep(.fc-col-header),
:deep(.fc-daygrid-day),
:deep(.fc-timegrid-slot),
:deep(.fc-toolbar),
:deep(.fc-header-toolbar) {
  position: relative;
  z-index: 1 !important;
}

/* Override any global FullCalendar z-index settings */
:deep([class*='fc-']) {
  z-index: 1 !important;
}

/* Special handling for modal overlap */
.calendar-container:has(~ *[class*='modal']),
.calendar-container:has(+ *[class*='modal']) {
  z-index: 0 !important;
}
</style>
