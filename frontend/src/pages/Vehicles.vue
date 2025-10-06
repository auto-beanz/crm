<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Vehicles" />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="vehicles"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Vehicle"
  />
  <VehiclesListView
    ref="vehiclesListView"
    v-if="vehicles.data && rows.length"
    v-model="vehicles.data.page_length_count"
    v-model:list="vehicles"
    :rows="rows"
    :columns="vehicles.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: vehicles.data.row_count,
      totalCount: vehicles.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div
    v-else-if="vehicles.data"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <VehiclesIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Vehicles')]) }}</span>
    </div>
  </div>
</template>

<script setup>
import VehiclesIcon from '@/components/Icons/VehiclesIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import VehiclesListView from '@/components/ListViews/VehiclesListView.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { formatDate, timeAgo } from '@/utils'
import { computed, ref } from 'vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('Vehicle')

const vehiclesListView = ref(null)

// vehicles data is loaded in the ViewControls component
const vehicles = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const rows = computed(() => {
  if (
    !vehicles.value?.data?.data ||
    !['list', 'group_by'].includes(vehicles.value.data.view_type)
  )
    return []

  return vehicles.value?.data.data.map((vehicle) => {
    let _rows = {}
    vehicles.value?.data.rows.forEach((row) => {
      _rows[row] = vehicle[row]

      let fieldType = vehicles.value?.data.columns?.find(
        (col) => (col.key || col.value) == row,
      )?.type

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(vehicle[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, vehicle)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, vehicle)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, vehicle)
      }

      if (row == 'license_plate') {
        _rows[row] = {
          label: vehicle.license_plate,
          image_label: vehicle.license_plate,
        }
      } else if (row == 'make') {
        _rows[row] = {
          label: vehicle.make,
        }
      } else if (row == 'model') {
        _rows[row] = {
          label: vehicle.model,
        }
      } else if (row == 'fuel_type') {
        _rows[row] = {
          label: vehicle.fuel_type,
          color: getFuelTypeColor(vehicle.fuel_type),
        }
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(vehicle[row]),
          timeAgo: __(timeAgo(vehicle[row])),
        }
      }
    })
    return _rows
  })
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
</script>
