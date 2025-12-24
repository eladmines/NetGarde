export const FORM_MODE = {
  CREATE: 'create',
  EDIT: 'edit',
} as const;

export type FormMode = typeof FORM_MODE[keyof typeof FORM_MODE];

