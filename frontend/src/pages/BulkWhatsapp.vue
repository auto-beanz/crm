<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="[{ label: 'Bulk Whatsapp' }]" />
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="showCreateModal = true"
      />
    </template>
  </LayoutHeader>
  
  <ViewControls
    ref="viewControls"
    v-model="bulkMessages"
    v-model:loadMore="loadMore"
    doctype="Bulk WhatsApp Message"
    :filters="{ docstatus: 0 }"
    :options="{
      allowedViews: ['list', 'group_by'],
    }"
  />
  
  <BulkWhatsappListView
    v-if="bulkMessages.data && rows.length"
    v-model:list="bulkMessages"
    :rows="rows"
    :columns="bulkMessages.data.columns"
    :options="{
      rowCount: bulkMessages.data.row_count,
      totalCount: bulkMessages.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @selectionsChanged="(selections) => viewControls.updateSelections(selections)"
  />
  
  <div v-else-if="bulkMessages.data" class="flex h-full items-center justify-center">
    <div class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4">
      <MessageSquareIcon class="h-10 w-10" /> <span>{{ __('No Bulk Messages Found') }}</span>
      <Button
        :label="__('Create')"
        iconLeft="plus"
        @click="showCreateModal = true"
      />
    </div>
  </div>

  <BulkWhatsappModal
    v-if="showCreateModal"
    v-model="showCreateModal"
    @created="() => bulkMessages.reload()"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import BulkWhatsappListView from '@/components/ListViews/BulkWhatsappListView.vue'
import BulkWhatsappModal from '@/components/Modals/BulkWhatsappModal.vue'
import { Breadcrumbs, Button } from 'frappe-ui'
import { ref, computed } from 'vue'
import { MessageSquareIcon } from 'lucide-vue-next' // Using a new icon

const showCreateModal = ref(false)
const bulkMessages = ref({}) // This will be filled by ViewControls
const loadMore = ref(1)
const viewControls = ref(null)

// Computed property to parse rows, similar to Leads.vue
const rows = computed(() => {
  if (!bulkMessages.value?.data?.data) return []
  return parseRows(bulkMessages.value.data.data)
})

function parseRows(data) {
  // Simple 1-to-1 mapping for now.
  // You can add custom logic here like in Leads.vue
  return data.map(doc => ({
    name: doc.name,
    title: doc.title,
    status: doc.status,
    recipient_count: doc.recipient_count,
    sent_count: doc.sent_count,
    scheduled_time: doc.scheduled_time,
  }))
}
</script>