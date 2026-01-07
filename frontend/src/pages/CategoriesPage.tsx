import Box from '@mui/material/Box';
import CategoriesTable from '../features/categories/components/table/CategoriesTable';
import CategoryFormDialog from '../features/categories/components/CategoryFormDialog';
import DeleteCategoryDialog from '../features/categories/components/DeleteCategoryDialog';
import CategoriesHeader from '../features/categories/components/CategoriesHeader';
import { useCategories } from '../features/categories/hooks/useCategories';
import { useCategoryForm } from '../features/categories/hooks/useCategoryForm';
import { useCategoryActions } from '../features/categories/hooks/useCategoryActions';

export default function CategoriesPage() {
  const { categories, loading, fetchCategories } = useCategories();
  const {
    openDialog,
    dialogMode,
    formData,
    submitting,
    setFormData,
    handleOpenCreateDialog,
    handleOpenEditDialog,
    handleCloseDialog,
    handleSubmit,
  } = useCategoryForm(fetchCategories);

  const {
    deleteDialogOpen,
    categoryToDelete,
    deleting,
    handleOpenDeleteDialog,
    handleCloseDeleteDialog,
    handleConfirmDelete,
  } = useCategoryActions(fetchCategories);

  const handleEdit = (categoryId: number) => {
    const category = categories.find((item) => item.id === categoryId);
    if (!category) {
      console.warn(`Category with id ${categoryId} not found`);
      return;
    }
    handleOpenEditDialog(category);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
      <CategoriesHeader onAddClick={handleOpenCreateDialog} />

      <CategoriesTable
        categories={categories}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleOpenDeleteDialog}
      />

      <CategoryFormDialog
        open={openDialog}
        mode={dialogMode}
        formData={formData}
        submitting={submitting}
        onClose={handleCloseDialog}
        onSubmit={handleSubmit}
        onFormDataChange={setFormData}
      />

      <DeleteCategoryDialog
        open={deleteDialogOpen}
        category={categoryToDelete}
        onClose={handleCloseDeleteDialog}
        onConfirm={handleConfirmDelete}
        deleting={deleting}
      />
    </Box>
  );
}

