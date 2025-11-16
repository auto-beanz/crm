<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('Create Bulk Message') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() && !isMobileView"
              variant="ghost"
              class="w-7"
              :tooltip="__('Edit fields layout')"
              :icon="EditIcon"
              @click="openQuickEntryModal"
            />
            <Button
              variant="ghost"
              class="w-7"
              @click="show = false"
              icon="x"
            />
          </div>
        </div>
        <div>
          <FieldLayout
            v-if="tabs.data"
            :tabs="tabs.data"
            :data="bulkMessage.doc"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="insertMessage.loading"
            @click="createBulkMessage"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { createResource, Dialog, Button, ErrorMessage, toast } from 'frappe-ui'
import { useDocument } from '@/data/document'
import { ref, onMounted, nextTick, provide } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  defaults: Object,
})

const { getUser, isManager } = usersStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)

const { document: bulkMessage, triggerOnChange } = useDocument('Bulk WhatsApp Message')

provide('triggerOnChange', triggerOnChange)

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'Bulk WhatsApp Message'],
  params: { doctype: 'Bulk WhatsApp Message', type: 'Quick Entry' },
  auto: true,
  transform: (_tabs) => {
    // This ensures child tables are initialized as empty arrays
    return _tabs.forEach((tab) => {
      tab.sections.forEach((section) => {
        section.columns.forEach((column) => {
          column.fields.forEach((field) => {
            if (field.fieldtype === 'Table') {
              bulkMessage.doc[field.fieldname] = []
            }
          })
        })
      })
    })
  },
})

const insertMessage = createResource({
  url: 'frappe.client.insert',
})

async function createBulkMessage() {
  insertMessage.submit(
    {
      doc: {
        doctype: 'Bulk WhatsApp Message',
        ...bulkMessage.doc,
      },
    },
    {
      validate() {
        error.value = null
        const doc = bulkMessage.doc
        // --- Basic Validation ---
        if (!doc.title) {
          error.value = 'Title is mandatory'
          return error.value
        }
        if (doc.recipient_type === 'Individual' && !(doc.recipients && doc.recipients.length > 0)) {
          error.value = 'Please add at least one recipient'
          return error.value
        }
        if (doc.recipient_type === 'Recipient List' && !doc.recipient_list) {
          error.value = 'Please select a recipient list'
          return error.value
        }
        if (doc.use_template && !doc.template) {
          error.value = 'Please select a template'
          return error.value
        }
      },
      onSuccess(data) {
        toast.success('Bulk Message created.')
        show.value = false
        
        // Auto-submit the document to queue it
        frappe.call('frappe.client.submit', {
          doctype: 'Bulk WhatsApp Message',
          name: data.name
        }).then(() => {
           toast.info('Bulk Message submitted for processing.')
           // Redirect to the new detail page
           router.push({ name: 'BulkWhatsappMessage', params: { id: data.name } })
        }).catch((err) => {
           toast.error('Failed to auto-submit document.')
        })
      },
      onError(err) {
        if (!err.messages) {
          error.value = err.message
          return
        }
        error.value = err.messages.join('\n')
      },
    },
  )
}

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'Bulk WhatsApp Message' }
  nextTick(() => (show.value = false))
}

onMounted(() => {
  
  bulkMessage.doc = { 
    recipient_type: 'Individual',
    use_template: 1,
    recipients: [],
  }
  Object.assign(bulkMessage.doc, props.defaults)
})
</script>