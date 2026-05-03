// 1. Get current *direct* user permissions in the Shared Drive
const currentPermissions = Drive.Permissions.list(folderId, {
  supportsAllDrives: true,
  fields: 'permissions(emailAddress, role, type, permissionDetails)'
}).permissions;
