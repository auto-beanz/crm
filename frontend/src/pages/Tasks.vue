<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Tasks" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="tasksListView?.customListActions"
        :actions="tasksListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createTask"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="tasks"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Task"
    :options="{
      allowedViews: ['list', 'kanban', 'calendar'],
    }"
  />
  <KanbanView
    v-if="$route.params.viewType == 'kanban' && rows.length"
    v-model="tasks"
    :options="{
      onClick: (row) => showTask(row.name),
      onNewClick: (column) => createTask(column),
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <template #title="{ titleField, itemName }">
      <div class="flex items-center gap-2">
        <div v-if="titleField === 'status'">
          <TaskStatusIcon :status="getRow(itemName, titleField).label" />
        </div>
        <div v-else-if="titleField === 'priority'">
          <TaskPriorityIcon :priority="getRow(itemName, titleField).label" />
        </div>
        <div v-else-if="titleField === 'assigned_to'">
          <Avatar
            v-if="getRow(itemName, titleField).full_name"
            class="flex items-center"
            :image="getRow(itemName, titleField).user_image"
            :label="getRow(itemName, titleField).full_name"
            size="sm"
          />
        </div>
        <div
          v-if="['modified', 'creation'].includes(titleField)"
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, titleField).label">
            <div>{{ getRow(itemName, titleField).timeAgo }}</div>
          </Tooltip>
        </div>
        <div
          v-else-if="getRow(itemName, titleField).label"
          class="truncate text-base"
        >
          {{ getRow(itemName, titleField).label }}
        </div>
        <div class="text-ink-gray-4" v-else>{{ __('No Title') }}</div>
      </div>
    </template>
    <template #fields="{ fieldName, itemName }">
      <div
        v-if="getRow(itemName, fieldName).label"
        class="truncate flex items-center gap-2"
      >
        <div v-if="fieldName === 'status'">
          <TaskStatusIcon
            class="size-3"
            :status="getRow(itemName, fieldName).label"
          />
        </div>
        <div v-else-if="fieldName === 'priority'">
          <TaskPriorityIcon :priority="getRow(itemName, fieldName).label" />
        </div>
        <div v-else-if="fieldName === 'assigned_to'">
          <Avatar
            v-if="getRow(itemName, fieldName).full_name"
            class="flex items-center"
            :image="getRow(itemName, fieldName).user_image"
            :label="getRow(itemName, fieldName).full_name"
            size="sm"
          />
        </div>
        <div
          v-if="['modified', 'creation'].includes(fieldName)"
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, fieldName).label">
            <div>{{ getRow(itemName, fieldName).timeAgo }}</div>
          </Tooltip>
        </div>
        <div
          v-else-if="fieldName == 'description'"
          class="truncate text-base max-h-44"
        >
          <TextEditor
            v-if="getRow(itemName, fieldName).label"
            :content="getRow(itemName, fieldName).label"
            :editable="false"
            editor-class="!prose-sm max-w-none focus:outline-none"
            class="flex-1 overflow-hidden"
          />
        </div>
        <div v-else class="truncate text-base">
          {{ getRow(itemName, fieldName).label }}
        </div>
      </div>
    </template>
    <template #actions="{ itemName }">
      <div class="flex gap-2 items-center justify-between">
        <div>
          <Button
            v-if="getRow(itemName, 'reference_docname').label"
            class="-ml-2"
            variant="ghost"
            size="sm"
            :label="
              getRow(itemName, 'reference_doctype').label == 'CRM Deal'
                ? __('Deal')
                : __('Lead')
            "
            :iconRight="ArrowUpRightIcon"
            @click.stop="
              redirect(
                getRow(itemName, 'reference_doctype').label,
                getRow(itemName, 'reference_docname').label,
              )
            "
          />
        </div>
        <Dropdown
          class="flex items-center gap-2"
          :options="actions(itemName)"
          variant="ghost"
          @click.stop.prevent
        >
          <Button icon="more-horizontal" variant="ghost" />
        </Dropdown>
      </div>
    </template>
  </KanbanView>
  <Calendar
    v-else-if="$route.params.viewType == 'calendar' && rows.length"
    :events="calendarEvents"
    :config="{ defaultMode: 'Month', isEditMode: false }"
    :onCellClick="(data) => createTaskOnDate(data.date)"
    class="calendar-view-container"
    :class="{ 'modal-open': showTaskModal }"
  />
  <TasksListView
    ref="tasksListView"
    v-else-if="tasks.data && rows.length"
    v-model="tasks.data.page_length_count"
    v-model:list="tasks"
    :rows="rows"
    :columns="tasks.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: tasks.data.row_count,
      totalCount: tasks.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @showTask="showTask"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div v-else-if="tasks.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <Email2Icon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Tasks')]) }}</span>
      <Button
        :label="__('Create')"
        iconLeft="plus"
        @click="showTaskModal = true"
      />
    </div>
  </div>
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    v-model:reloadTasks="tasks"
    :task="task"
  />
</template>

<script setup>
import CustomActions from '@/components/CustomActions.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import TaskPriorityIcon from '@/components/Icons/TaskPriorityIcon.vue'
import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import TasksListView from '@/components/ListViews/TasksListView.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { formatDate, timeAgo } from '@/utils'
import { Avatar, Dropdown, TextEditor, Tooltip, call } from 'frappe-ui'
import Calendar from 'frappe-ui/src/components/Calendar/Calendar.vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Task')
const { getUser } = usersStore()

const router = useRouter()

const tasksListView = ref(null)

// tasks data is loaded in the ViewControls component
const tasks = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object') {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

// Transform tasks data for frappe-ui Calendar
const calendarEvents = computed(() => {
  if (!tasks.value?.data?.data) return []

  const taskData = tasks.value.data.data
  const allTasks = Array.isArray(taskData)
    ? taskData
    : taskData.flatMap((column) => column.data || [])

  const events = allTasks
    .filter((task) => task.due_date) // Only show tasks with due dates
    .map((task) => {
      // Get color based on status
      const getStatusColor = (status) => {
        const colors = {
          Backlog: 'gray',
          Todo: 'blue',
          'In Progress': 'orange',
          Done: 'green',
          Cancelled: 'red',
        }
        return colors[status] || 'gray'
      }

      const event = {
        id: task.name,
        title: task.title || 'Untitled Task',
        fromDate: task.due_date.split(' ')[0],
        toDate: task.due_date.split(' ')[0],
        fromTime: task.due_date.split(' ')[1] || '00:00',
        toTime: task.due_date.split(' ')[1] || '23:59',
        color: getStatusColor(task.status),
        isFullDay: true,
        // Store additional task data for event handlers
        taskData: {
          status: task.status,
          priority: task.priority,
          assigned_to: task.assigned_to,
          description: task.description,
          reference_doctype: task.reference_doctype,
          reference_docname: task.reference_docname,
          custom_type: task.custom_type,
        },
      }
      return event
    })

  return events
})

const rows = computed(() => {
  if (!tasks.value?.data?.data) return []

  if (tasks.value.data.view_type === 'kanban') {
    return getKanbanRows(tasks.value.data.data, tasks.value.data.fields)
  }

  openTaskFromURL()
  return parseRows(tasks.value?.data.data, tasks.value?.data.columns)
})

function getKanbanRows(data, columns) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      _rows.push(row)
    })
  })
  return parseRows(_rows, columns)
}

function parseRows(rows, columns = []) {
  let view_type = tasks.value.data.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rows.map((task) => {
    let _rows = {}
    tasks.value?.data.rows.forEach((row) => {
      _rows[row] = task[row]

      let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
        type
      ]

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation', 'due_date'].includes(row)
      ) {
        _rows[row] = formatDate(task[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, task)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, task)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, task)
      }

      if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(task[row]),
          timeAgo: __(timeAgo(task[row])),
        }
      } else if (row == 'assigned_to') {
        _rows[row] = {
          label: task.assigned_to && getUser(task.assigned_to).full_name,
          ...(task.assigned_to && getUser(task.assigned_to)),
        }
      }
    })
    return _rows
  })
}

const showTaskModal = ref(false)

const task = ref({
  name: '',
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Backlog',
  priority: 'Low',
  reference_doctype: 'CRM Lead',
  reference_docname: '',
  custom_type: '',
})

function showTask(name) {
  console.log({ name })
  console.log(rows.value)
  let t = rows.value?.find((row) => row.name === name)
  console.log({ t })
  task.value = {
    name: t.name,
    title: t.title,
    description: t.description,
    assigned_to: t.assigned_to?.email || '',
    due_date: t.due_date,
    status: t.status,
    priority: t.priority,
    custom_type: t.custom_type,
    reference_doctype: t.reference_doctype,
    reference_docname: t.reference_docname,
  }
  showTaskModal.value = true
}

function createTask(column) {
  task.value = {
    name: '',
    title: '',
    description: '',
    assigned_to: '',
    due_date: '',
    status: 'Backlog',
    priority: 'Low',
    reference_doctype: 'CRM Lead',
    reference_docname: '',
    custom_type: '',
  }

  if (column.column?.name) {
    let column_field = tasks.value.params.column_field
    if (column_field) {
      task.value[column_field] = column.column.name
    }
  }

  showTaskModal.value = true
}

function createTaskOnDate(date) {
  // Handle both Date object and string formats
  const dateStr = date instanceof Date ? date.toISOString().split('T')[0] : date

  task.value = {
    name: '',
    title: '',
    description: '',
    assigned_to: '',
    due_date: dateStr, // Format date as YYYY-MM-DD
    status: 'Backlog',
    priority: 'Low',
    reference_doctype: 'CRM Lead',
    reference_docname: '',
    custom_type: '',
  }
  showTaskModal.value = true
}

function actions(name) {
  return [
    {
      label: __('Delete'),
      icon: 'trash-2',
      onClick: () => {
        deletetask(name)
        tasks.value.reload()
      },
    },
  ]
}

async function deletetask(name) {
  await call('frappe.client.delete', {
    doctype: 'CRM Task',
    name,
  })
}

function redirect(doctype, docname) {
  if (!docname) return
  let name = doctype == 'CRM Deal' ? 'Deal' : 'Lead'
  let params = { leadId: docname }
  if (name == 'Deal') {
    params = { dealId: docname }
  }
  router.push({ name: name, params: params })
}

const openTaskFromURL = () => {
  const searchParams = new URLSearchParams(window.location.search)
  const taskName = searchParams.get('open')

  if (taskName && rows.value?.length) {
    showTask(parseInt(taskName))
    searchParams.delete('open')
    window.history.replaceState(null, '', window.location.pathname)
  }
}
</script>

<style scoped>
/* When modal is open, hide calendar or reduce its interactivity */
.calendar-view-container.modal-open {
  z-index: 0 !important;
  pointer-events: none;
  opacity: 0.5;
  filter: blur(1px);
}
</style>
