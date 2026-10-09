from django.contrib import admin

from .models import Achievement, Education, Profile, Project, ProjectDocument, ProjectImage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Profile.objects.exists()  # one profile only


admin.site.register(Education)
admin.site.register(Achievement)


class ImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


class DocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published", "order", "date")
    list_filter = ("category", "published")
    list_editable = ("published", "order")
    search_fields = ("title", "summary", "tech")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ImageInline, DocumentInline]
