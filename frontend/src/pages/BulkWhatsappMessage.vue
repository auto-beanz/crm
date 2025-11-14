<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    
    <template v-if="doc.name" #right-header>
      <template v-if="doc.docstatus === 1">
        <Button
          :label="__('Check Progress')"
          @click="checkProgress"
          :loading="progressResource.loading"
        />
        <Button
          variant="secondary"
          theme="red"
          :label="__('Retry Failed')"
          @click="retryFailed"
          :loading="retryResource.loading"
        />
      </template>
      
      <Button
        v-if="doc.docstatus === 0"
        variant="solid"
        :label="__('Submit')"
        @click="submitDoc"
        :loading="document.save.loading"
      />
    </template>
  </LayoutHeader>
  
  <div v-if="doc.name" class="flex h-full overflow-hidden">
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-panel>
        <div v-if="tabs[tabIndex].name === 'Recipients'" class="p-4">
          <h3 class="mb-4 text-lg font-semibold">{{ __('Recipients') }}</h3>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  {{ __('Mobile Number') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  {{ __('Name') }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="recipient in doc.recipients" :key="recipient.name">
                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                  {{ recipient.mobile_number }}
                </td>
                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                  {{ recipient.recipient_name }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="tabs[tabIndex].name === 'Messages'" class="p-4">
          <h3 class="mb-4 text-lg font-semibold">{{ __('Message Log') }}</h3>
          <ListView
            :columns="messageLog.data.columns"
            :rows="messageLogRows"
            v-if="messageLog.data"
          />
        </div>
      </template>
    </Tabs>

    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div class="flex-1 overflow-y-auto p-6">
        <h2 class="mb-4 text-xl font-semibold">{{ doc.title }}</h2>
        <div class="flex flex-col gap-4">
          <FormControl
            :label="__('Status')"
            type="text"
            :modelValue="doc.status"
            :disabled="true"
          />
          <FormControl
            :label="__('Template')"
            type="link"
            doctype="WhatsApp Templates"
            :modelValue="doc.template"
            :disabled="true"
          />
          <FormControl
            :label="__('Recipient List')"
            type="link"
            doctype="WhatsApp Recipient List"
            :modelValue="doc.recipient_list"
            :disabled="true"
            v-if="doc.recipient_type === 'Recipient List'"
          />
          <FormControl
            :label="__('Recipient Count')"
            type="text"
            :modelValue="doc.recipient_count"
            :disabled="true"
          />
          <FormControl
            :label="__('Sent Count')"
            type="text"
            :modelValue="doc.sent_count"
            :disabled="true"
          />
          <FormControl
            :label="__('Scheduled Time')"
            type="datetime"
            :modelValue="doc.scheduled_time"
            :disabled="true"
          />
        </div>
      </div>
    </Resizer>
  </div>
  
  <ErrorPage v-else-if="errorTitle" :errorTitle="errorTitle" :errorMessage="errorMessage" />
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import { useDocument } from '@/data/document'
import { Breadcrumbs, Button, Tabs, FormControl, ListView, createResource, toast } from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MessageSquareIcon, SendIcon, UserIcon } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const tabIndex = ref(0)
const errorTitle = ref('')
const errorMessage = ref('')

// Fetch the main Bulk WhatsApp Message document
const { document, error } = useDocument('Bulk WhatsApp Message', props.id)
const doc = computed(() => document.doc || {})

// Breadcrumbs
const breadcrumbs = computed(() => [
  { label: __('Bulk Whatsapp'), route: { name: 'BulkWhatsapp' } },
  { label: doc.value.title || props.id },
])

// Tabs
const tabs = computed(() => [
  { name: 'Recipients', label: __('Recipients'), icon: UserIcon },
  { name: 'Messages', label: __('Message Log'), icon: SendIcon },
])

// --- API Calls for Buttons ---

// Resource for "Check Progress"
const progressResource = createResource({
  url: 'frappe_whatsapp.frappe_whatsapp.doctype.bulk_whatsapp_message.bulk_whatsapp_message.get_progress',
  makeParams: () => ({ name: props.id }),
})

function checkProgress() {
  progressResource.submit({
    onSuccess(progress) {
      let html = `
        <p>${__('Total')}: ${progress.total}</p>
        <p>${__('Sent')}: ${progress.sent}</p>
        <p>${__('Failed')}: ${progress.failed}</p>
        <p>${__('Queued')}: ${progress.queued}</p>
        <strong>${Math.round(progress.percent)}% ${__('Complete')}</strong>
      `
      frappe.msgprint({
        title: __('Message Progress'),
        indicator: 'blue',
        message: html,
      })
    },
    onError(err) {
      toast.error(err.messages?.[0] || 'Error fetching progress')
    }
  })
}

// Resource for "Retry Failed"
const retryResource = createResource({
  url: 'frappe_whatsapp.frappe_whatsapp.doctype.bulk_whatsapp_message.bulk_whatsapp_message.retry_failed',
  makeParams: () => ({ name: props.id }),
})

function retryFailed() {
  retryResource.submit({
    onSuccess() {
      toast.success('Failed messages have been requeued')
      document.reload()
    },
    onError(err) {
      toast.error(err.messages?.[0] || 'Error retrying messages')
    }
  })
}

// Function to Submit a Draft
function submitDoc() {
  document.save.submit({
    onSuccess() {
      toast.success('Document submitted and queued for sending.')
      document.reload()
    },
    onError(err) {
      toast.error(err.messages?.[0] || 'Submission failed')
    }
  })
}

// Resource to fetch the individual sent messages
const messageLog = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'WhatsApp Message',
    fields: '["name", "to", "status", "message_id", "message_type"]',
    filters: {
      bulk_message_reference: props.id
    }
  },
  auto: true
})
const messageLogRows = computed(() => messageLog.data.data || [])

// Watch for errors (e.g., Not Found)
watch(error, (err) => {
  if (err) {
    errorTitle.value = __(
      err.exc_type == 'DoesNotExistError' ? 'Document not found' : 'Error'
    )
    errorMessage.value = __(err.messages?.[0] || 'An error occurred')
  }
})
</script>