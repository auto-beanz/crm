<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template v-if="!errorTitle" #right-header>
      <CustomActions
        v-if="document._actions?.length"
        :actions="document._actions"
      />
      <CustomActions
        v-if="document.actions?.length"
        :actions="document.actions"
      />
      <AssignTo
        v-model="assignees.data"
        doctype="Vehicle"
        :docname="vehicleId"
      />
    </template>
  </LayoutHeader>
  <div v-if="doc.name" class="flex h-full overflow-hidden">
    <Resizer side="right" class="flex flex-col justify-between border-l">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
        @click="copyToClipboard(vehicleId)"
      >
        {{ __(vehicleId) }}
      </div>
      <div class="flex items-center justify-start gap-5 border-b p-5">
        <Tooltip :text="__('Vehicle')">
          <div class="group relative size-12">
            <div
              class="flex size-12 items-center justify-center rounded-full bg-ink-gray-3"
            >
              <VehicleIcon class="h-6 w-6 text-ink-gray-7" />
            </div>
          </div>
        </Tooltip>
        <div class="flex flex-col gap-2.5 truncate text-ink-gray-9">
          <Tooltip :text="doc.license_plate">
            <div class="truncate text-2xl font-medium">
              {{ doc.license_plate }}
            </div>
          </Tooltip>
          <div class="text-lg text-ink-gray-7">
            {{ doc.make }} {{ doc.model }}
          </div>
        </div>
      </div>

      <!-- Vehicle Details Section -->
      <div class="flex-1 overflow-y-auto p-5">
        <div class="space-y-6">
          <!-- Basic Information -->
          <div>
            <h3 class="text-lg font-medium text-ink-gray-9 mb-3">
              {{ __('Basic Information') }}
            </h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Make') }}</span>
                <span class="font-medium">{{ doc.make }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Model') }}</span>
                <span class="font-medium">{{ doc.model }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Fuel Type') }}</span>
                <Badge
                  v-if="doc.fuel_type"
                  :label="doc.fuel_type"
                  :color="getFuelTypeColor(doc.fuel_type)"
                />
              </div>
            </div>
          </div>

          <!-- Vehicle Details -->
          <div>
            <h3 class="text-lg font-medium text-ink-gray-9 mb-3">
              {{ __('Vehicle Details') }}
            </h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Odometer (Last)') }}</span>
                <span class="font-medium"
                  >{{ formatNumber(doc.last_odometer) }} km</span
                >
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Vehicle Value') }}</span>
                <span class="font-medium">{{
                  formatCurrency(doc.vehicle_value)
                }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Location') }}</span>
                <span class="font-medium">{{ doc.location || '-' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Chassis No') }}</span>
                <span class="font-medium">{{ doc.chassis_no || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Insurance Details -->
          <div v-if="doc.insurance_company || doc.policy_no">
            <h3 class="text-lg font-medium text-ink-gray-9 mb-3">
              {{ __('Insurance Details') }}
            </h3>
            <div class="space-y-3">
              <div v-if="doc.insurance_company" class="flex justify-between">
                <span class="text-ink-gray-7">{{
                  __('Insurance Company')
                }}</span>
                <span class="font-medium">{{ doc.insurance_company }}</span>
              </div>
              <div v-if="doc.policy_no" class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Policy No') }}</span>
                <span class="font-medium">{{ doc.policy_no }}</span>
              </div>
              <div v-if="doc.start_date" class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('Start Date') }}</span>
                <span class="font-medium">{{
                  formatDate(doc.start_date)
                }}</span>
              </div>
              <div v-if="doc.end_date" class="flex justify-between">
                <span class="text-ink-gray-7">{{ __('End Date') }}</span>
                <span class="font-medium">{{ formatDate(doc.end_date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Resizer>
  </div>
</template>

<script setup>
import AssignTo from '@/components/AssignTo.vue'
import CustomActions from '@/components/CustomActions.vue'
import Icon from '@/components/Icon.vue'
import VehicleIcon from '@/components/Icons/VehicleIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Resizer from '@/components/Resizer.vue'
import { useDocument } from '@/data/document'
import { copyToClipboard, formatDate } from '@/utils'
import {
  Badge,
  Breadcrumbs,
  createDocumentResource,
  createListResource,
  Tooltip,
} from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  vehicleId: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const errorTitle = ref(null)

const vehicle = createDocumentResource({
  doctype: 'Vehicle',
  name: props.vehicleId,
  auto: true,
})

const assignees = createListResource({
  doctype: 'ToDo',
  fields: ['name', 'allocated_to as user', 'description'],
  filters: {
    reference_type: 'Vehicle',
    reference_name: props.vehicleId,
    status: ['!=', 'Cancelled'],
  },
  auto: true,
  transform: (data) => {
    return data.map((row) => {
      return {
        ...row,
        user: row.user,
      }
    })
  },
})

const { document, reload } = useDocument('Vehicle', props.vehicleId)

const doc = computed(() => vehicle.doc || {})

const tabIndex = ref(0)
const tabs = [
  {
    name: 'activity',
    label: 'Activity',
    icon: 'activity',
  },
]

const breadcrumbs = computed(() => {
  let items = [
    {
      label: 'Vehicles',
      route: { name: 'Vehicles' },
      icon: 'car',
    },
  ]
  if (doc.value?.license_plate) {
    items.push({
      label: doc.value.license_plate,
      route: { name: 'Vehicle', params: { vehicleId: props.vehicleId } },
    })
  }
  return items
})

function getFuelTypeColor(fuelType) {
  const colorMap = {
    Petrol: 'orange',
    Diesel: 'blue',
    'Natural Gas': 'green',
    Electric: 'purple',
  }
  return colorMap[fuelType] || 'gray'
}

function formatNumber(value) {
  if (!value) return '0'
  return new Intl.NumberFormat().format(value)
}

function formatCurrency(value) {
  if (!value) return ''
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value)
}

function reloadAssignees() {
  assignees.reload()
}

// Set tab based on hash
watch(
  () => route.hash,
  (hash) => {
    if (hash) {
      let tab = hash.slice(1)
      let foundTabIndex = tabs.findIndex((t) => t.name === tab)
      if (foundTabIndex !== -1) {
        tabIndex.value = foundTabIndex
      }
    }
  },
  { immediate: true },
)
</script>
