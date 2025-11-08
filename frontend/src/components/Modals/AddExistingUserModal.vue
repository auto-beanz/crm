<template>
  <Dialog v-model="show" :options="{ title: __('Add Existing User') }" @close="show = false">
    <template #body-content>
      <div class="flex gap-1 border rounded mb-4 p-2 text-ink-gray-5">
        <FeatherIcon name="info" class="size-3.5" />
        <p class="text-sm">
          {{
            __(
              'Add existing system users to this CRM. Assign them a role to grant access with their current credentials.',
            )
          }}
        </p>
      </div>

      <FormControl
        type="select"
        class="mb-4"
        v-model="selectedCompany"
        :label="__('Company')"
        :options="companiesList.data || []"
        :loading="companiesList.loading"
        placeholder="Select a Company"
      />

      <FormControl
        type="select"
        class="mb-4"
        v-model="selectedDepartment"
        :label="__('Team / Department')"
        :options="departmentsList.data || []"
        :loading="departmentsList.loading"
        :disabled="!selectedCompany"
        :placeholder="
          selectedCompany
            ? __('Select a Team')
            : __('Please select a company first')
        "
      />

      <label class="block text-xs text-ink-gray-5 mb-1.5">
        {{ __('Users') }}
      </label>

      <div class="p-2 group bg-surface-gray-2 hover:bg-surface-gray-3 rounded">
        <MultiSelectUserInput
          v-if="selectedDepartment"
          class="flex-1"
          inputClass="!bg-surface-gray-2 hover:!bg-surface-gray-3 group-hover:!bg-surface-gray-3"
          :placeholder="__('john@doe.com')"
          v-model="newUsers"
          :validate="validateEmail"
          :optionsList="departmentUsers.data"
          :fetchUsers="false"
          :existingEmails="['admin@example.com']"
          :error-message="
            (value) => __('{0} is an invalid email address', [value])
          "
        />
      </div>
      <FormControl
        type="select"
        class="mt-4"
        v-model="role"
        :label="__('Role')"
        :options="roleOptions"
        :description="description"
      />
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button variant="solid" :label="__('Add')" :disabled="!newUsers.length" @click="addNewUser.submit()"
          :loading="addNewUser.loading" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import MultiSelectUserInput from '@/components/Controls/MultiSelectUserInput.vue'
import { validateEmail } from '@/utils'
import { usersStore } from '@/stores/users'
import { createResource, toast } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const { users, isAdmin, isManager } = usersStore()

const show = defineModel()

const newUsers = ref([])
const role = ref('Sales User')
const selectedCompany = ref(null)
const selectedDepartment = ref(null)

const companiesList = createResource({
  url: 'crm.api.user.get_selectable_companies', 
  auto: true,
  transform: (data) => data,
})

const departmentsList = createResource({
  url: 'crm.api.user.get_departments_for_company',
  makeParams: () => {
    return { company: selectedCompany.value }
  },
  auto: false,
  disable: () => !selectedCompany.value,
  transform: (data) => data,
})

const departmentUsers = createResource({
  url: 'crm.api.user.get_users_for_department',
  makeParams: () => {
    return { department: selectedDepartment.value }
  },
  auto: false,
  transform: (data) => data,
})

watch(selectedCompany, (newCompany) => {
  selectedDepartment.value = null
  newUsers.value = []
  if (newCompany) {
    departmentsList.reload()
  } else {
    departmentsList.data = []
  }
})

watch(selectedDepartment, (newDept) => {
  newUsers.value = []
  if (newDept) {
    departmentUsers.reload()
  } else {
    departmentUsers.data = []
  }
})

const description = computed(() => {
  return {
    'System Manager':
      'Can manage all aspects of the CRM, including user management, customizations and settings.',
    'Sales Manager':
      'Can manage and invite new users, and create public & private views (reports).',
    'Sales User':
      'Can work with leads and deals and create private views (reports).',
    'Aftersales Executive':
      'Can work with leads and deals and create private views (reports) - aftersales.',
    'Customer Support Executive':
      'Can work with leads and deals and create private views (reports). - customer support.',
    'Business Development Executive':
      'Can work with leads and deals and create private views (reports). - business development.',
  }[role.value]
})

const roleOptions = computed(() => {
  return [
    { value: 'Sales User', label: __('Sales Executive') },
    { value: 'Aftersales Executive', label: __('Aftersales Executive') },
    { value: 'Customer Support Executive', label: __('Customer Support Executive') },
    { value: 'Business Development Executive', label: __('Business Development Executive') },
    ...(isManager() ? [{ value: 'Sales Manager', label: __('Manager') }] : []),
    ...(isAdmin() ? [{ value: 'System Manager', label: __('Admin') }] : []),
  ]
})

const addNewUser = createResource({
  url: 'crm.api.user.add_existing_users',
  makeParams: () => ({
    users: JSON.stringify(newUsers.value),
    role: role.value,
  }),
  onSuccess: () => {
    toast.success(__('Users added successfully'))
    newUsers.value = []
    show.value = false
    users.reload()
  },
  onError: (error) => {
    toast.error(error.messages[0] || __('Failed to add users'))
  },
})
</script>
