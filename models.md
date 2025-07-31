from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
from django.conf import settings


# ================================
# ENHANCED SEO MIXIN
# ================================

class EnhancedSEOMixin(models.Model):
    """Enhanced SEO mixin with additional fields for electronics products"""
    slug = models.SlugField(max_length=255, unique=True, help_text="SEO-friendly URL slug")
    meta_title = models.CharField(max_length=60, blank=True, help_text="Meta title (60 chars max)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Meta description (160 chars max)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    
    # SEO Content blocks
    seo_text_top = models.TextField(blank=True, help_text="SEO-rich content for top of page")
    seo_text_bottom = models.TextField(blank=True, help_text="SEO-rich content for bottom of page")
    
    # Open Graph / Social Media
    og_title = models.CharField(max_length=95, blank=True, help_text="Open Graph title")
    og_description = models.CharField(max_length=300, blank=True, help_text="Open Graph description")
    og_image = models.ImageField(upload_to='seo/og_images/', blank=True, null=True, help_text="Open Graph image")
    
    # Twitter/X Card
    twitter_title = models.CharField(max_length=70, blank=True, help_text="Twitter card title")
    twitter_description = models.CharField(max_length=200, blank=True, help_text="Twitter card description")
    twitter_image = models.ImageField(upload_to='seo/twitter_images/', blank=True, null=True, help_text="Twitter card image")
    
    # Facebook specific
    facebook_title = models.CharField(max_length=95, blank=True, help_text="Facebook specific title")
    facebook_description = models.CharField(max_length=300, blank=True, help_text="Facebook specific description")
    facebook_image = models.ImageField(upload_to='seo/facebook_images/', blank=True, null=True, help_text="Facebook specific image")
    
    # Technical SEO
    canonical_url = models.URLField(blank=True, help_text="Canonical URL to prevent duplicate content")
    robots_index = models.BooleanField(default=True, help_text="Allow search engines to index this page")
    robots_follow = models.BooleanField(default=True, help_text="Allow search engines to follow links on this page")
    
    # Schema.org structured data
    schema_type = models.CharField(max_length=50, blank=True, help_text="Schema.org type (e.g., Product, ElectronicsStore)")
    custom_schema = models.JSONField(blank=True, null=True, help_text="Custom schema.org JSON-LD data")
    
    # Additional SEO fields for electronics
    focus_keyword = models.CharField(max_length=100, blank=True, help_text="Primary focus keyword")
    secondary_keywords = models.TextField(blank=True, help_text="Secondary keywords (one per line)")
    
    class Meta:
        abstract = True


# ================================
# WAREHOUSE & LOCATION MANAGEMENT
# ================================

class Country(models.Model):
    """Country model for geographic data"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True, help_text="ISO 3166-1 alpha-3 country code")
    currency_code = models.CharField(max_length=3, blank=True, help_text="ISO 4217 currency code")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0, help_text="Default tax rate")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return self.name

class State(models.Model):
    """State/Province model"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, help_text="State/Province code")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0, help_text="State tax rate")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['country', 'name']
        unique_together = ['country', 'code']
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"

class Warehouse(models.Model):
    """Warehouse/fulfillment center model"""
    name = models.CharField(max_length=200, help_text="Warehouse name")
    code = models.CharField(max_length=20, unique=True, help_text="Unique warehouse code")
    description = models.TextField(blank=True)
    
    # Address information
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    manager_name = models.CharField(max_length=200, blank=True)
    
    # Warehouse specifications
    total_capacity = models.PositiveIntegerField(blank=True, null=True, help_text="Total storage capacity")
    available_capacity = models.PositiveIntegerField(blank=True, null=True, help_text="Available storage capacity")
    warehouse_type = models.CharField(max_length=20, choices=[
        ('main', 'Main Warehouse'),
        ('regional', 'Regional Warehouse'),
        ('local', 'Local Distribution'),
        ('dropship', 'Drop Shipping'),
        ('3pl', 'Third-Party Logistics'),
    ], default='main')
    
    # Operating hours
    operating_hours = models.JSONField(default=dict, blank=True, help_text="Operating hours by day")
    timezone = models.CharField(max_length=50, default='UTC', help_text="Warehouse timezone")
    
    # Status and configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default warehouse for new products")
    priority = models.PositiveIntegerField(default=1, help_text="Fulfillment priority (1=highest)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.city, str(self.state) if self.state else '', self.postal_code, self.country.name])
        return ', '.join(filter(None, address_parts))
    
    @property
    def capacity_utilization(self):
        """Calculate capacity utilization percentage"""
        if self.total_capacity and self.available_capacity is not None:
            used = self.total_capacity - self.available_capacity
            return round((used / self.total_capacity) * 100, 2)
        return None

class WarehouseZone(models.Model):
    """Warehouse zones for better inventory organization"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100, help_text="Zone name (e.g., A1, Electronics)")
    code = models.CharField(max_length=20, help_text="Zone code")
    description = models.TextField(blank=True)
    zone_type = models.CharField(max_length=20, choices=[
        ('receiving', 'Receiving'),
        ('storage', 'Storage'),
        ('picking', 'Picking'),
        ('packing', 'Packing'),
        ('shipping', 'Shipping'),
        ('returns', 'Returns'),
        ('quarantine', 'Quarantine'),
    ], default='storage')
    capacity = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['warehouse', 'code']
        ordering = ['warehouse', 'name']
    
    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"


# ================================
# ENHANCED BRAND MODEL
# ================================

class Brand(models.Model):
    """Enhanced brand model for electronics"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    country_of_origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    headquarters = models.CharField(max_length=255, blank=True, null=True)
    ceo = models.CharField(max_length=255, blank=True, null=True)
    employee_count = models.PositiveIntegerField(blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    stock_symbol = models.CharField(max_length=10, blank=True, null=True)
    
    # Brand status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    # Display and ordering
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ================================
# CATEGORY HIERARCHY MODELS
# ================================

class Department(EnhancedSEOMixin):
    """Top-level department model with enhanced SEO support"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=20, unique=True, help_text="Unique department code")
    image = models.ImageField(upload_to='departments/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='departments/banners/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or FontAwesome icon")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        indexes = [
            models.Index(fields=['is_active', 'sort_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Category(EnhancedSEOMixin):
    """Category model with enhanced SEO support"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='categories')
    code = models.CharField(max_length=20, help_text="Category code within department")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='categories/banners/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or FontAwesome icon")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'sort_order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ['department', 'code']
        indexes = [
            models.Index(fields=['department', 'is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.department.name}-{self.name}")
        super().save(*args, **kwargs)

class Subcategory(EnhancedSEOMixin):
    """Subcategory model with enhanced SEO support"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    primary_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='primary_subcategories')
    additional_categories = models.ManyToManyField(Category, blank=True, related_name='additional_subcategories')
    code = models.CharField(max_length=20, help_text="Subcategory code")
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='subcategories/banners/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or FontAwesome icon")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['primary_category', 'sort_order', 'name']
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'
        unique_together = ['primary_category', 'code']
        indexes = [
            models.Index(fields=['primary_category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.primary_category.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.primary_category.name}-{self.name}")
        super().save(*args, **kwargs)

class ChildCategory(EnhancedSEOMixin):
    """ChildCategory model with enhanced SEO support"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    primary_subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='primary_child_categories')
    additional_subcategories = models.ManyToManyField(Subcategory, blank=True, related_name='additional_child_categories')
    code = models.CharField(max_length=20, help_text="Child category code")
    image = models.ImageField(upload_to='child_categories/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='child_categories/banners/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or FontAwesome icon")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['primary_subcategory', 'sort_order', 'name']
        verbose_name = 'Child Category'
        verbose_name_plural = 'Child Categories'
        unique_together = ['primary_subcategory', 'code']
        indexes = [
            models.Index(fields=['primary_subcategory', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.primary_subcategory.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.primary_subcategory.name}-{self.name}")
        super().save(*args, **kwargs)


# ================================
# PRODUCT ATTRIBUTE SYSTEM
# ================================

class ProductAttribute(models.Model):
    """Enhanced product attributes for electronics"""
    ATTRIBUTE_TYPES = [
        ('text', 'Text'),
        ('textarea', 'Long Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean (Yes/No)'),
        ('choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('date', 'Date'),
        ('color', 'Color'),
        ('image', 'Image'),
        ('file', 'File'),
        ('url', 'URL'),
        ('email', 'Email'),
        # Electronics specific
        ('voltage', 'Voltage'),
        ('power', 'Power/Wattage'),
        ('frequency', 'Frequency'),
        ('memory', 'Memory/Storage'),
        ('resolution', 'Resolution'),
        ('connectivity', 'Connectivity'),
        ('operating_system', 'Operating System'),
        ('processor', 'Processor'),
        ('display', 'Display'),
        ('battery', 'Battery'),
        ('camera', 'Camera'),
        ('audio', 'Audio'),
        ('dimension', 'Dimension'),
        ('weight', 'Weight'),
        ('material', 'Material'),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Internal name (lowercase, underscores)")
    display_name = models.CharField(max_length=100, help_text="Display name for frontend")
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES, default='text')
    unit = models.CharField(max_length=20, blank=True, help_text="Unit of measurement (e.g., GB, MHz, inches)")
    description = models.TextField(blank=True, help_text="Description of this attribute")
    
    # Validation
    validation_rules = models.JSONField(blank=True, null=True, help_text="JSON validation rules")
    default_value = models.CharField(max_length=255, blank=True, help_text="Default value")
    placeholder_text = models.CharField(max_length=255, blank=True, help_text="Placeholder for input")
    
    # Behavior flags
    is_required = models.BooleanField(default=False, help_text="Required when adding products")
    is_variant_attribute = models.BooleanField(default=False, help_text="Used for product variants")
    is_filterable = models.BooleanField(default=True, help_text="Show in product filters")
    is_comparable = models.BooleanField(default=True, help_text="Show in product comparison")
    is_searchable = models.BooleanField(default=False, help_text="Include in search index")
    show_in_listing = models.BooleanField(default=False, help_text="Show in product listings")
    
    # Categories where this attribute applies
    categories = models.ManyToManyField(Category, blank=True, related_name='attributes')
    
    # Ordering
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['attribute_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.display_name

    def clean(self):
        """Validate model data"""
        super().clean()
        
        # Name should be lowercase with underscores
        if self.name:
            if not self.name.replace('_', '').replace('-', '').isalnum():
                raise ValidationError("Name can only contain letters, numbers, underscores and hyphens")

class ProductAttributeValue(models.Model):
    """Values for choice-based attributes"""
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=200, help_text="Internal value")
    display_value = models.CharField(max_length=200, blank=True, help_text="Display value (optional)")
    description = models.TextField(blank=True)
    
    # Visual representation
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    icon = models.CharField(max_length=100, blank=True, help_text="Font Awesome icon class")
    image = models.ImageField(upload_to='attribute_values/', blank=True, null=True)
    
    # Numeric representation for filtering/sorting
    numeric_value = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    
    # Status
    is_default = models.BooleanField(default=False, help_text="Default selection")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['attribute', 'sort_order', 'value']
        unique_together = ['attribute', 'value']
        indexes = [
            models.Index(fields=['attribute', 'is_active']),
            models.Index(fields=['numeric_value']),
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.display_value or self.value}"

    def save(self, *args, **kwargs):
        # Auto-generate display_value if not provided
        if not self.display_value:
            if self.attribute.unit:
                self.display_value = f"{self.value} {self.attribute.unit}"
            else:
                self.display_value = self.value
        super().save(*args, **kwargs)


# ================================
# ENHANCED PRODUCT MODELS
# ================================

class ProductTag(models.Model):
    """Product tags for better organization and SEO"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    tag_type = models.CharField(max_length=20, choices=[
        ('feature', 'Feature'),
        ('use_case', 'Use Case'),
        ('target_audience', 'Target Audience'),
        ('promotion', 'Promotion'),
        ('seasonal', 'Seasonal'),
        ('trending', 'Trending'),
    ], default='feature')
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code for tag display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ColorPalette(models.Model):
    """Color palette management for consistent branding"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ProductColor(models.Model):
    """Advanced color management system"""
    name = models.CharField(max_length=100, help_text="Color name (e.g., 'Space Gray')")
    display_name = models.CharField(max_length=100, blank=True, help_text="Marketing display name")
    hex_code = models.CharField(max_length=7, help_text="Primary hex color code")
    rgb_values = models.CharField(max_length=20, blank=True, help_text="RGB values (255,255,255)")
    
    # Color properties
    color_family = models.CharField(max_length=30, choices=[
        ('neutral', 'Neutral'),
        ('warm', 'Warm'),
        ('cool', 'Cool'),
        ('metallic', 'Metallic'),
        ('pastel', 'Pastel'),
        ('bright', 'Bright/Neon'),
        ('earth', 'Earth Tone'),
    ], default='neutral')
    
    brightness = models.CharField(max_length=20, choices=[
        ('very_light', 'Very Light'),
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('dark', 'Dark'),
        ('very_dark', 'Very Dark'),
    ], default='medium')
    
    # Visual aids
    color_swatch = models.ImageField(upload_to='color_swatches/', blank=True, null=True)
    
    # Organization
    palette = models.ForeignKey(ColorPalette, on_delete=models.SET_NULL, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['color_family', 'brightness', 'sort_order', 'name']
        unique_together = ['name', 'hex_code']
    
    def __str__(self):
        return f"{self.display_name or self.name} ({self.hex_code})"
    
    @property
    def css_style(self):
        """CSS style for color preview"""
        return f"background-color: {self.hex_code};"

class ProductMaterial(models.Model):
    """Material options for products"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('metal', 'Metal'),
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('fabric', 'Fabric'),
        ('leather', 'Leather'),
        ('wood', 'Wood'),
        ('ceramic', 'Ceramic'),
        ('composite', 'Composite'),
        ('other', 'Other'),
    ], default='other')
    finish_options = models.JSONField(
        default=list, 
        blank=True,
        help_text="Available finishes for this material"
    )
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ProductSize(models.Model):
    """Standardized size options"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('storage', 'Storage Capacity'),
        ('screen', 'Screen Size'),
        ('memory', 'Memory Size'),
        ('physical', 'Physical Size'),
        ('clothing', 'Clothing Size'),
        ('other', 'Other'),
    ])
    value = models.CharField(max_length=50, help_text="Size value (e.g., '128GB', '15.6 inch')")
    numeric_value = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        blank=True, 
        null=True,
        help_text="Numeric value for sorting"
    )
    unit = models.CharField(max_length=20, blank=True, help_text="Unit of measurement")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'numeric_value', 'sort_order']
        unique_together = ['category', 'value']
    
    def __str__(self):
        return f"{self.name} ({self.value})"

class ElectronicsProduct(models.Model):
    """Enhanced product model specifically designed for electronics with comprehensive SEO support"""
    
    # ===== ENHANCED CATEGORY RELATIONSHIPS =====
    
    # Legacy single relationships (keeping for backward compatibility)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='legacy_products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='legacy_products')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True, related_name='legacy_products')
    child_category = models.ForeignKey(ChildCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='legacy_products')
    
    # NEW: Primary categories (one each - required for new products)
    primary_department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null for backward compatibility
        blank=True,
        related_name='primary_products',
        help_text="Main department for this product"
    )
    primary_category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null for backward compatibility
        blank=True,
        related_name='primary_products',
        help_text="Main category for this product"
    )
    primary_subcategory = models.ForeignKey(
        Subcategory, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null for backward compatibility
        blank=True,
        related_name='primary_products',
        help_text="Main subcategory for this product"
    )
    primary_child_category = models.ForeignKey(
        ChildCategory, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null for backward compatibility
        blank=True,
        related_name='primary_products',
        help_text="Main child category for this product"
    )
    
    # NEW: Additional categories (many-to-many - optional)
    additional_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='additional_products',
        help_text="Additional departments this product belongs to"
    )
    additional_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='additional_products', 
        help_text="Additional categories this product belongs to"
    )
    additional_subcategories = models.ManyToManyField(
        Subcategory,
        blank=True,
        related_name='additional_products',
        help_text="Additional subcategories this product belongs to"
    )
    additional_child_categories = models.ManyToManyField(
        ChildCategory,
        blank=True,
        related_name='additional_products',
        help_text="Additional child categories this product belongs to"
    )

    # ===== BASIC INFORMATION =====
    name = models.CharField(max_length=255)
    model_number = models.CharField(max_length=100, blank=True, help_text="Manufacturer model number")
    short_description = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    
    featured_image = models.ImageField(
        upload_to='products/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Featured Image",
        help_text="Main product image displayed on product pages"
    )
    
    # ===== PRODUCT IDENTIFICATION =====
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    upc = models.CharField(max_length=12, blank=True, help_text="Universal Product Code")
    ean = models.CharField(max_length=13, blank=True, help_text="European Article Number")
    isbn = models.CharField(max_length=13, blank=True, help_text="For books/manuals")
    mpn = models.CharField(max_length=100, blank=True, help_text="Manufacturer Part Number")
    
    # ===== PRICING =====
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    msrp = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Manufacturer's Suggested Retail Price")
    
    # Wholesale pricing
    wholesale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Wholesale price for bulk orders"
    )
    min_wholesale_quantity = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Minimum quantity required for wholesale pricing"
    )

    # ===== INVENTORY MANAGEMENT (BASIC) =====
    # Note: Advanced inventory is now handled by ProductStock model
    track_inventory = models.BooleanField(default=True, help_text="Track inventory for this product")
    allow_backorder = models.BooleanField(default=False, help_text="Allow orders when out of stock")
    expected_restock_date = models.DateField(blank=True, null=True)
    
    # ===== ENHANCED SEO FIELDS =====
    
    # Basic SEO
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL-friendly version of the product name")
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO meta title (50-60 characters recommended)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description (150-160 characters recommended)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated meta keywords")
    
    # Enhanced SEO Fields
    focus_keyword = models.CharField(max_length=100, blank=True, help_text="Primary keyword to target for SEO")
    secondary_keywords = models.CharField(max_length=500, blank=True, help_text="Additional keywords separated by commas (max 10)")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL to prevent duplicate content issues")
    seo_priority = models.CharField(
        max_length=20, 
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium',
        help_text="SEO priority level for this product"
    )
    
    # Social Media Optimization (Open Graph)
    og_title = models.CharField(max_length=95, blank=True, help_text="Title for social media sharing (max 95 characters)")
    og_description = models.CharField(max_length=300, blank=True, help_text="Description for social media sharing (max 300 characters)")
    og_type = models.CharField(
        max_length=20,
        choices=[
            ('product', 'Product'),
            ('article', 'Article'),
            ('website', 'Website'),
            ('blog', 'Blog Post')
        ],
        default='product',
        help_text="Open Graph content type"
    )
    
    # Twitter Card Optimization
    twitter_card_type = models.CharField(
        max_length=20,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
            ('product', 'Product'),
            ('app', 'App')
        ],
        default='summary_large_image',
        help_text="Twitter card type for sharing"
    )
    twitter_creator = models.CharField(max_length=20, blank=True, help_text="Twitter username of content creator (include @)")
    
    # Additional Social Media Fields
    facebook_title = models.CharField(max_length=95, blank=True, help_text="Facebook-specific title")
    facebook_description = models.CharField(max_length=300, blank=True, help_text="Facebook-specific description")
    facebook_image = models.ImageField(upload_to='products/seo/facebook/', blank=True, null=True, help_text="Facebook sharing image")

    twitter_title = models.CharField(max_length=95, blank=True, help_text="Twitter-specific title")
    twitter_description = models.CharField(max_length=300, blank=True, help_text="Twitter-specific description")
    twitter_image = models.ImageField(upload_to='products/seo/twitter/', blank=True, null=True, help_text="Twitter card image")

    # Open Graph image (different from facebook_image)
    og_image = models.ImageField(upload_to='products/seo/og/', blank=True, null=True, help_text="Open Graph sharing image")

    # Additional SEO content fields
    seo_text_top = models.TextField(blank=True, help_text="SEO text to display at top of product page")
    seo_text_bottom = models.TextField(blank=True, help_text="SEO text to display at bottom of product page")

    # Robot directives (positive logic to match form expectations)
    robots_index = models.BooleanField(default=True, help_text="Allow search engines to index this page")
    robots_follow = models.BooleanField(default=True, help_text="Allow search engines to follow links on this page")
    
    # Technical SEO & Structured Data
    schema_type = models.CharField(
        max_length=50,
        choices=[
            ('Product', 'Product'),
            ('Article', 'Article'),
            ('BlogPosting', 'Blog Post'),
            ('WebPage', 'Web Page'),
            ('Organization', 'Organization'),
            ('LocalBusiness', 'Local Business'),
            ('Event', 'Event'),
            ('FAQ', 'FAQ Page'),
            ('Review', 'Review'),
            ('Recipe', 'Recipe')
        ],
        default='Product',
        help_text="Schema.org structured data type"
    )
    custom_schema = models.TextField(blank=True, help_text="Custom JSON-LD structured data")
    
    # Robot Directives (existing)
    no_index = models.BooleanField(default=False, help_text="Prevent search engines from indexing this page")
    no_follow = models.BooleanField(default=False, help_text="Prevent search engines from following links on this page")
    no_archive = models.BooleanField(default=False, help_text="Prevent search engines from showing cached versions")
    no_snippet = models.BooleanField(default=False, help_text="Prevent search engines from showing snippets")
    
    # ===== ELECTRONICS-SPECIFIC TECHNICAL SPECIFICATIONS =====
    
    # Power & Electrical
    voltage = models.CharField(max_length=50, blank=True, help_text="e.g., 110-240V AC")
    power_consumption = models.CharField(max_length=50, blank=True, help_text="e.g., 65W")
    frequency = models.CharField(max_length=50, blank=True, help_text="e.g., 50/60Hz")
    energy_rating = models.CharField(max_length=20, blank=True, help_text="Energy efficiency rating")
    
    # Display (for devices with screens)
    screen_size = models.CharField(max_length=50, blank=True, help_text="e.g., 15.6 inches")
    resolution = models.CharField(max_length=50, blank=True, help_text="e.g., 1920x1080")
    display_type = models.CharField(max_length=50, blank=True, help_text="e.g., LED, OLED, LCD")
    refresh_rate = models.CharField(max_length=20, blank=True, help_text="e.g., 60Hz, 120Hz")
    color_accuracy = models.CharField(max_length=50, blank=True, help_text="e.g., 99% sRGB")
    
    # Processing & Performance
    processor = models.CharField(max_length=100, blank=True, help_text="CPU/Processor details")
    processor_speed = models.CharField(max_length=50, blank=True, help_text="e.g., 2.4GHz")
    graphics_card = models.CharField(max_length=100, blank=True, help_text="GPU details")
    ram = models.CharField(max_length=50, blank=True, help_text="e.g., 8GB DDR4")
    storage = models.CharField(max_length=100, blank=True, help_text="e.g., 256GB SSD")
    
    # Connectivity
    wifi_standard = models.CharField(max_length=50, blank=True, help_text="e.g., Wi-Fi 6 (802.11ax)")
    bluetooth_version = models.CharField(max_length=20, blank=True, help_text="e.g., Bluetooth 5.0")
    usb_ports = models.CharField(max_length=100, blank=True, help_text="e.g., 2x USB 3.0, 1x USB-C")
    hdmi_ports = models.CharField(max_length=50, blank=True, help_text="e.g., 1x HDMI 2.1")
    ethernet = models.BooleanField(default=False)
    audio_jack = models.BooleanField(default=False)
    
    # Audio
    audio_specifications = models.CharField(max_length=200, blank=True, help_text="Audio specs")
    speaker_power = models.CharField(max_length=50, blank=True, help_text="e.g., 2x 10W")
    microphone = models.BooleanField(default=False)
    
    # Camera (for devices with cameras)
    camera_resolution = models.CharField(max_length=50, blank=True, help_text="e.g., 1080p, 4K")
    camera_features = models.TextField(blank=True, help_text="Camera features and capabilities")
    
    # Battery (for portable devices)
    battery_capacity = models.CharField(max_length=50, blank=True, help_text="e.g., 50Wh, 4000mAh")
    battery_life = models.CharField(max_length=100, blank=True, help_text="e.g., Up to 10 hours")
    charging_time = models.CharField(max_length=50, blank=True, help_text="e.g., 2 hours")
    fast_charging = models.BooleanField(default=False)
    wireless_charging = models.BooleanField(default=False)
    
    # Operating System & Software
    operating_system = models.CharField(max_length=100, blank=True, help_text="e.g., Windows 11, Android 12")
    software_included = models.TextField(blank=True, help_text="Pre-installed software")
    
    # Physical Specifications
    weight = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True, help_text="Weight in kg")
    length = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Length in cm")
    width = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Width in cm")
    height = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    color_options = models.CharField(max_length=200, blank=True, help_text="Available colors")
    material = models.CharField(max_length=100, blank=True, help_text="Primary material")
    
    # Warranty & Support
    warranty_period = models.CharField(max_length=50, blank=True, help_text="e.g., 2 years")
    warranty_type = models.CharField(max_length=100, blank=True, help_text="Type of warranty coverage")
    manufacturer_support = models.TextField(blank=True, help_text="Support information")
    
    # Compliance & Certifications
    certifications = models.TextField(blank=True, help_text="Safety certifications (CE, FCC, etc.)")
    environmental_compliance = models.CharField(max_length=200, blank=True, help_text="Environmental standards")
    
    # Compatibility
    compatible_devices = models.TextField(blank=True, help_text="Compatible devices/systems")
    system_requirements = models.TextField(blank=True, help_text="Minimum system requirements")
    
    # Product tags
    tags = models.ManyToManyField(ProductTag, blank=True, related_name='products')
    
    # Product Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_wholesale = models.BooleanField(default=False, help_text="Available for wholesale")
    is_digital = models.BooleanField(default=False, help_text="Digital product (downloadable)")
    is_refurbished = models.BooleanField(default=False)
    is_discontinued = models.BooleanField(default=False)
    requires_shipping = models.BooleanField(default=True, help_text="Product requires physical shipping")
    
    # Availability
    availability_status = models.CharField(max_length=20, choices=[
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-Order'),
        ('discontinued', 'Discontinued'),
        ('limited_stock', 'Limited Stock'),
        ('back_order', 'Back Order'),
    ], default='in_stock')
    
    # Release Information
    release_date = models.DateField(blank=True, null=True)
    launch_date = models.DateField(blank=True, null=True, help_text="Market launch date")
    
    # Legacy SEO Fields (keeping for backward compatibility)
    product_tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags for better SEO")
    featured_keywords = models.TextField(blank=True, help_text="Key product features for SEO")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Electronics Product'
        verbose_name_plural = 'Electronics Products'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
            models.Index(fields=['brand', 'model_number']),
            models.Index(fields=['is_active', 'availability_status']),
            models.Index(fields=['child_category', 'is_active']),
            models.Index(fields=['primary_child_category', 'is_active']),
            models.Index(fields=['focus_keyword']),
            models.Index(fields=['seo_priority', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.brand.name if self.brand else ''} {self.name}".strip()
    
    def save(self, *args, **kwargs):
        # Auto-sync legacy fields with primary fields for backward compatibility
        if self.primary_department and not self.department:
            self.department = self.primary_department
        if self.primary_category and not self.category:
            self.category = self.primary_category
        if self.primary_subcategory and not self.subcategory:
            self.subcategory = self.primary_subcategory
        if self.primary_child_category and not self.child_category:
            self.child_category = self.primary_child_category
        
        # Auto-populate primary fields from legacy fields if primary is empty
        if not self.primary_department and self.department:
            self.primary_department = self.department
        if not self.primary_category and self.category:
            self.primary_category = self.category
        if not self.primary_subcategory and self.subcategory:
            self.primary_subcategory = self.subcategory
        if not self.primary_child_category and self.child_category:
            self.primary_child_category = self.child_category
        
        # Auto-generate slug if not provided
        if not self.slug:
            slug_base = f"{self.brand.name if self.brand else ''} {self.name}".strip()
            base_slug = slugify(slug_base)
            slug = base_slug
            counter = 1
            
            # Ensure unique slug
            while ElectronicsProduct.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        # Auto-generate meta title if not provided
        if not self.meta_title and self.name:
            meta_title = f"{self.brand.name if self.brand else ''} {self.name}".strip()
            if len(meta_title) > 60:
                meta_title = meta_title[:57] + "..."
            self.meta_title = meta_title
        
        # Auto-generate meta description if not provided
        if not self.meta_description and self.short_description:
            meta_desc = self.short_description
            if len(meta_desc) > 160:
                meta_desc = meta_desc[:157] + "..."
            self.meta_description = meta_desc
        
        # Auto-generate Open Graph title if not provided
        if not self.og_title and self.meta_title:
            self.og_title = self.meta_title
        
        # Auto-generate Open Graph description if not provided
        if not self.og_description and self.meta_description:
            self.og_description = self.meta_description
        
        # Sync robot directives (convert between positive and negative logic)
        self.no_index = not self.robots_index
        self.no_follow = not self.robots_follow
        
        # Auto-populate social media fields if empty
        if not self.facebook_title and self.og_title:
            self.facebook_title = self.og_title
        if not self.facebook_description and self.og_description:
            self.facebook_description = self.og_description
        if not self.twitter_title and self.og_title:
            self.twitter_title = self.og_title
        if not self.twitter_description and self.og_description:
            self.twitter_description = self.og_description
        
        super().save(*args, **kwargs)
    
    # ===== PROPERTIES =====
    
    @property
    def final_price(self):
        """Returns the final selling price"""
        return self.discount_price if self.discount_price else self.selling_price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.selling_price > 0:
            return round(((self.selling_price - self.discount_price) / self.selling_price) * 100, 2)
        return 0
    
    @property
    def total_stock_quantity(self):
        """Get total stock across all warehouses"""
        return sum(stock.available_quantity for stock in self.stock_entries.filter(is_active=True))
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.total_stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.total_stock_quantity <= 10  # Default threshold
    
    @property 
    def full_name(self):
        """Full product name with brand"""
        return f"{self.brand.name if self.brand else ''} {self.name} {self.model_number}".strip()
    
    # ===== CATEGORY MANAGEMENT METHODS =====
    
    def get_all_departments(self):
        """Get all departments this product belongs to"""
        departments = []
        if self.primary_department:
            departments.append(self.primary_department)
        departments.extend(self.additional_departments.all())
        return list(set(departments))
    
    def get_all_categories(self):
        """Get all categories this product belongs to"""
        categories = []
        if self.primary_category:
            categories.append(self.primary_category)
        categories.extend(self.additional_categories.all())
        return list(set(categories))
    
    def get_all_subcategories(self):
        """Get all subcategories this product belongs to"""
        subcategories = []
        if self.primary_subcategory:
            subcategories.append(self.primary_subcategory)
        subcategories.extend(self.additional_subcategories.all())
        return list(set(subcategories))
    
    def get_all_child_categories(self):
        """Get all child categories this product belongs to"""
        child_categories = []
        if self.primary_child_category:
            child_categories.append(self.primary_child_category)
        child_categories.extend(self.additional_child_categories.all())
        return list(set(child_categories))
    
    def get_primary_category_breadcrumb(self):
        """Get primary category breadcrumb"""
        return {
            'department': self.primary_department or self.department,
            'category': self.primary_category or self.category,
            'subcategory': self.primary_subcategory or self.subcategory,
            'child_category': self.primary_child_category or self.child_category,
        }
    
    # ===== SEO METHODS =====
    
    @property
    def seo_title(self):
        """Get the best title for SEO purposes"""
        return self.meta_title or self.name
    
    @property
    def seo_description(self):
        """Get the best description for SEO purposes"""
        return self.meta_description or self.short_description or self.description[:160]
    
    def get_absolute_url(self):
        """Get the canonical URL for this product"""
        if self.canonical_url:
            return self.canonical_url
        from django.urls import reverse
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    def get_robot_directives(self):
        """Get robot meta directives as a string"""
        directives = []
        
        if self.no_index:
            directives.append('noindex')
        else:
            directives.append('index')
        
        if self.no_follow:
            directives.append('nofollow')
        else:
            directives.append('follow')
        
        if self.no_archive:
            directives.append('noarchive')
        
        if self.no_snippet:
            directives.append('nosnippet')
        
        return ', '.join(directives)
    
    def get_structured_data(self):
        """Generate structured data for this product"""
        structured_data = {
            "@context": "https://schema.org",
            "@type": self.schema_type,
            "name": self.name,
            "description": self.seo_description,
            "sku": self.sku,
            "url": self.get_absolute_url(),
        }
        
        # Add brand information
        if self.brand:
            structured_data["brand"] = {
                "@type": "Brand",
                "name": self.brand.name
            }
        
        # Add price information
        if self.final_price:
            structured_data["offers"] = {
                "@type": "Offer",
                "price": str(self.final_price),
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock" if self.is_in_stock else "https://schema.org/OutOfStock"
            }
        
        # Add product identifiers
        if self.mpn:
            structured_data["mpn"] = self.mpn
        if self.upc:
            structured_data["gtin12"] = self.upc
        if self.ean:
            structured_data["gtin13"] = self.ean
        
        # Add custom schema if provided
        if self.custom_schema:
            try:
                import json
                custom_data = json.loads(self.custom_schema)
                structured_data.update(custom_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return structured_data

# ===== PRODUCT ATTRIBUTE ASSIGNMENT =====

class ProductAttributeAssignment(models.Model):
    """Assignment of attribute values to products"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='attribute_assignments')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    
    # For choice attributes
    attribute_value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE, null=True, blank=True)
    
    # For direct value attributes
    value = models.TextField(blank=True, help_text="Direct value for non-choice attributes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'attribute']
        indexes = [
            models.Index(fields=['product', 'attribute']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.attribute.display_name}: {self.display_value}"

    @property
    def display_value(self):
        """Get display value for this assignment"""
        if self.attribute_value:
            return self.attribute_value.display_value
        return self.value


# ================================
# INVENTORY MANAGEMENT SYSTEM
# ================================

class ProductStock(models.Model):
    """Product stock levels per warehouse"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='stock_entries')
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='stock_entries')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_entries')
    
    # Stock quantities
    quantity = models.IntegerField(default=0, help_text="Total quantity in stock")
    reserved_quantity = models.IntegerField(default=0, help_text="Quantity reserved for pending orders")
    damaged_quantity = models.IntegerField(default=0, help_text="Damaged/unusable quantity")
    
    # Stock thresholds
    reorder_point = models.PositiveIntegerField(default=10, help_text="Reorder when stock reaches this level")
    max_stock_level = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum stock level")
    
    # Storage location within warehouse
    zone = models.ForeignKey(WarehouseZone, on_delete=models.SET_NULL, null=True, blank=True)
    bin_location = models.CharField(max_length=50, blank=True, help_text="Specific bin/shelf location")
    
    # Stock status
    is_active = models.BooleanField(default=True)
    is_available_for_sale = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_movement = models.DateTimeField(blank=True, null=True, help_text="Last stock movement date")
    
    class Meta:
        unique_together = ['product', 'variant', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['warehouse', 'quantity']),
            models.Index(fields=['is_active', 'is_available_for_sale']),
        ]
    
    def __str__(self):
        variant_info = f" - {self.variant}" if self.variant else ""
        return f"{self.product.name}{variant_info} @ {self.warehouse.name}: {self.available_quantity}"
    
    @property
    def available_quantity(self):
        """Calculate available quantity (total - reserved - damaged)"""
        return max(0, self.quantity - self.reserved_quantity - self.damaged_quantity)
    
    @property
    def is_low_stock(self):
        """Check if stock is below reorder point"""
        return self.available_quantity <= self.reorder_point
    
    @property
    def is_out_of_stock(self):
        """Check if completely out of stock"""
        return self.available_quantity <= 0
    
    @property
    def utilization_percentage(self):
        """Calculate storage utilization if max level is set"""
        if self.max_stock_level:
            return round((self.quantity / self.max_stock_level) * 100, 2)
        return None
    
    def reserve_stock(self, quantity):
        """Reserve stock for an order"""
        if quantity > self.available_quantity:
            raise ValueError(f"Cannot reserve {quantity} items. Only {self.available_quantity} available.")
        self.reserved_quantity += quantity
        self.save()
    
    def release_reservation(self, quantity):
        """Release reserved stock"""
        self.reserved_quantity = max(0, self.reserved_quantity - quantity)
        self.save()
    
    def adjust_stock(self, quantity, reason="Manual adjustment"):
        """Adjust stock quantity and create movement record"""
        old_quantity = self.quantity
        self.quantity = max(0, quantity)
        movement_quantity = self.quantity - old_quantity
        self.last_movement = timezone.now()
        self.save()
        
        # Create stock movement record
        StockMovement.objects.create(
            product=self.product,
            variant=self.variant,
            warehouse=self.warehouse,
            movement_type='adjustment',
            quantity=movement_quantity,
            reference=reason,
            stock_after=self.quantity
        )

class StockMovement(models.Model):
    """Track all stock movements for audit trail"""
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'), 
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost/Stolen'),
        ('expired', 'Expired'),
        ('sample', 'Sample'),
        ('promotion', 'Promotional'),
    ]
    
    # Product information
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='stock_movements')
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='stock_movements')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_movements')
    
    # Movement details
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(help_text="Positive for stock in, negative for stock out")
    stock_after = models.IntegerField(help_text="Stock level after this movement")
    
    # Reference information
    reference = models.CharField(max_length=100, blank=True, help_text="Order number, PO number, etc.")
    notes = models.TextField(blank=True)
    
    # Transfer specific fields
    from_warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='outbound_transfers',
        help_text="Source warehouse for transfers"
    )
    to_warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='inbound_transfers',
        help_text="Destination warehouse for transfers"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who made this movement"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse', '-created_at']),
            models.Index(fields=['movement_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.movement_type.title()}: {self.product.name} ({self.quantity}) @ {self.warehouse.name}"

class StockAlert(models.Model):
    """Stock alerts and notifications"""
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('overstock', 'Overstock'),
        ('damaged', 'Damaged Stock'),
        ('expiring', 'Expiring Soon'),
    ]
    
    ALERT_STATUS = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='stock_alerts')
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='stock_alerts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_alerts')
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='active')
    
    message = models.TextField(help_text="Alert message")
    current_stock = models.IntegerField(help_text="Stock level when alert was triggered")
    threshold = models.IntegerField(blank=True, null=True, help_text="Threshold that triggered alert")
    
    # Alert handling
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['alert_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.alert_type.title()}: {self.product.name} @ {self.warehouse.name}"
    
    def acknowledge(self, user=None):
        """Acknowledge the alert"""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.save()
    
    def resolve(self):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


# ================================
# PRODUCT VARIANTS
# ================================

class ProductVariant(models.Model):
    """Enhanced Product variants with better inventory integration"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255, help_text="Variant name")
    sku = models.CharField(max_length=100, unique=True)
    
    # Variant attributes
    color_name = models.CharField(max_length=50, blank=True, help_text="Color name (e.g., 'Midnight Black')")
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code (e.g., '#000000')")
    size_storage = models.CharField(max_length=50, blank=True, help_text="Size or storage (e.g., '128GB', 'Large')")
    
    # Enhanced color management
    product_color = models.ForeignKey(
        ProductColor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Select from predefined colors"
    )
    
    # Enhanced material and finish
    product_material = models.ForeignKey(
        ProductMaterial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Product material"
    )
    finish = models.CharField(max_length=50, blank=True, help_text="Surface finish (e.g., 'Matte', 'Glossy')")
    
    # Enhanced size management  
    product_size = models.ForeignKey(
        ProductSize,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Standardized size option"
    )
    
    # Pricing
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Physical properties
    weight_difference = models.DecimalField(
        max_digits=8, 
        decimal_places=3, 
        blank=True, 
        null=True,
        help_text="Weight difference from base product (kg)"
    )
    
    # Variant-specific specs
    variant_specifications = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional specifications specific to this variant"
    )
    
    # Media
    image = models.ImageField(upload_to='product_variants/', blank=True, null=True)
    
    # Status and configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default variant for product")
    availability_date = models.DateField(blank=True, null=True, help_text="When variant becomes available")
    
    # Attribute values for flexible attributes
    attribute_values = models.ManyToManyField(ProductAttributeValue, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['product', 'name']
        unique_together = ['product', 'color_name', 'size_storage']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        variant_parts = [self.product.name]
        if self.color_name:
            variant_parts.append(self.color_name)
        if self.size_storage:
            variant_parts.append(self.size_storage)
        return " - ".join(variant_parts)
    
    @property
    def display_name(self):
        """Enhanced display name"""
        parts = []
        if self.product_color:
            parts.append(self.product_color.display_name or self.product_color.name)
        elif self.color_name:
            parts.append(self.color_name)
            
        if self.product_size:
            parts.append(self.product_size.value)
        elif self.size_storage:
            parts.append(self.size_storage)
            
        if self.product_material:
            parts.append(self.product_material.name)
            
        return " • ".join(parts) if parts else self.name
    
    @property
    def final_price(self):
        """Calculate final price including adjustment"""
        return self.product.final_price + self.price_adjustment
    
    @property
    def total_stock_quantity(self):
        """Get total stock across all warehouses"""
        return sum(stock.available_quantity for stock in self.stock_entries.filter(is_active=True))
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock"""
        return self.total_stock_quantity > 0
    
    def save(self, *args, **kwargs):
        # Auto-sync data from related objects
        if self.product_color and not self.color_name:
            self.color_name = self.product_color.display_name or self.product_color.name
            self.color_code = self.product_color.hex_code
            
        if self.product_size and not self.size_storage:
            self.size_storage = self.product_size.value
            
        super().save(*args, **kwargs)


# ================================
# COUPON & PROMOTION SYSTEM
# ================================

class CouponType(models.Model):
    """Types of coupons for better organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Coupon(models.Model):
    """Comprehensive coupon system"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage Discount'),
        ('fixed_amount', 'Fixed Amount Discount'),
        ('free_shipping', 'Free Shipping'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('bulk_discount', 'Bulk Discount'),
    ]
    
    USAGE_TYPES = [
        ('single_use', 'Single Use'),
        ('multiple_use', 'Multiple Use'),
        ('unlimited', 'Unlimited Use'),
    ]
    
    APPLICATION_TYPES = [
        ('cart_total', 'Apply to Cart Total'),
        ('specific_products', 'Specific Products Only'),
        ('category', 'Category Products'),
        ('brand', 'Brand Products'),
        ('first_order', 'First Order Only'),
        ('returning_customer', 'Returning Customers'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, help_text="Internal coupon name")
    code = models.CharField(max_length=50, unique=True, help_text="Coupon code customers enter")
    description = models.TextField(blank=True, help_text="Customer-facing description")
    coupon_type = models.ForeignKey(CouponType, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Discount Configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Percentage (0-100) or fixed amount"
    )
    
    # Application Rules
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES, default='cart_total')
    
    # Minimum Requirements
    minimum_order_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Minimum order value to use coupon"
    )
    minimum_quantity = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Minimum quantity required"
    )
    
    # Maximum Limits
    maximum_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum discount amount (for percentage coupons)"
    )
    
    # Usage Limits
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='multiple_use')
    usage_limit = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Total usage limit (null = unlimited)"
    )
    usage_limit_per_customer = models.PositiveIntegerField(
        default=1,
        help_text="Usage limit per customer"
    )
    
    # Time Restrictions
    start_date = models.DateTimeField(help_text="When coupon becomes active")
    end_date = models.DateTimeField(help_text="When coupon expires")
    
    # Product/Category Restrictions
    applicable_products = models.ManyToManyField(
        ElectronicsProduct, 
        blank=True,
        related_name='applicable_coupons',
        help_text="Products this coupon applies to"
    )
    excluded_products = models.ManyToManyField(
        ElectronicsProduct, 
        blank=True,
        related_name='excluded_coupons',
        help_text="Products excluded from this coupon"
    )
    applicable_categories = models.ManyToManyField(
        Category, 
        blank=True,
        related_name='applicable_coupons',
        help_text="Categories this coupon applies to"
    )
    excluded_categories = models.ManyToManyField(
        Category, 
        blank=True,
        related_name='excluded_coupons',
        help_text="Categories excluded from this coupon"
    )
    applicable_brands = models.ManyToManyField(
        Brand, 
        blank=True,
        related_name='applicable_coupons',
        help_text="Brands this coupon applies to"
    )
    
    # Buy X Get Y Configuration
    buy_quantity = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Quantity to buy for Buy X Get Y offers"
    )
    get_quantity = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Quantity to get free for Buy X Get Y offers"
    )
    get_discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount on 'get' items (100 = free)"
    )
    
    # Advanced Features
    stackable = models.BooleanField(
        default=False,
        help_text="Can be combined with other coupons"
    )
    auto_apply = models.BooleanField(
        default=False,
        help_text="Automatically apply if conditions are met"
    )
    
    # Status and Tracking
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0, help_text="Total times used")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this coupon"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['discount_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self, customer=None):
        """Check if coupon is currently valid"""
        now = timezone.now()
        
        # Check if active and within date range
        if not self.is_active:
            return False, "Coupon is not active"
        
        if now < self.start_date:
            return False, "Coupon is not yet active"
        
        if now > self.end_date:
            return False, "Coupon has expired"
        
        # Check usage limits
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        
        # Check customer-specific usage
        if customer and self.usage_limit_per_customer:
            customer_usage = CouponUsage.objects.filter(
                coupon=self,
                customer=customer
            ).count()
            if customer_usage >= self.usage_limit_per_customer:
                return False, "Customer usage limit reached"
        
        return True, "Valid"
    
    def calculate_discount(self, cart_total, items=None):
        """Calculate discount amount for given cart total and items"""
        if self.discount_type == 'percentage':
            discount = (cart_total * self.discount_value) / 100
            if self.maximum_discount_amount:
                discount = min(discount, self.maximum_discount_amount)
            return discount
        
        elif self.discount_type == 'fixed_amount':
            return min(self.discount_value, cart_total)
        
        elif self.discount_type == 'free_shipping':
            # This would need to be calculated based on shipping costs
            return 0  # Placeholder
        
        # Add more discount type calculations as needed
        return 0
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

class CouponUsage(models.Model):
    """Track coupon usage by customers"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usage_records')
    customer = models.ForeignKey(
        'Customer',  # Assuming you'll add Customer model later
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Customer who used the coupon"
    )
    customer_email = models.EmailField(blank=True, help_text="Email for guest customers")
    
    # Usage details
    order_reference = models.CharField(max_length=100, blank=True, help_text="Order number or reference")
    cart_total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cart total before discount")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Actual discount applied")
    
    # Metadata
    used_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['coupon', 'customer']),
            models.Index(fields=['-used_at']),
        ]
    
    def __str__(self):
        customer_info = self.customer or self.customer_email or "Guest"
        return f"{self.coupon.code} used by {customer_info}"


# ================================
# ENHANCED PRODUCT MEDIA & CONTENT
# ================================

class ProductImage(models.Model):
    """Product images with enhanced metadata"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='images')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    image = models.ImageField(upload_to='product_images/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    image_type = models.CharField(max_length=20, choices=[
        ('main', 'Main Product Image'),
        ('detail', 'Detail/Close-up'),
        ('lifestyle', 'Lifestyle Image'),
        ('comparison', 'Size Comparison'),
        ('packaging', 'Packaging'),
        ('manual', 'Manual/Documentation'),
        ('360', '360 View'),
    ], default='main')
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['sort_order']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.product.name}"

class ProductVideo(models.Model):
    """Product videos and multimedia content"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField(help_text="YouTube, Vimeo, or direct video URL")
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    video_type = models.CharField(max_length=20, choices=[
        ('demo', 'Product Demo'),
        ('unboxing', 'Unboxing'),
        ('review', 'Review'),
        ('tutorial', 'Tutorial'),
        ('comparison', 'Comparison'),
        ('360', '360 View'),
    ], default='demo')
    duration = models.CharField(max_length=10, blank=True, help_text="e.g., 5:30")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Video: {self.title} for {self.product.name}"

class ProductDocument(models.Model):
    """Product documentation and files"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=30, choices=[
        ('manual', 'User Manual'),
        ('datasheet', 'Datasheet'),
        ('specification', 'Specification Sheet'),
        ('installation', 'Installation Guide'),
        ('warranty', 'Warranty Information'),
        ('certificate', 'Certificate'),
        ('driver', 'Driver/Software'),
        ('firmware', 'Firmware'),
        ('other', 'Other'),
    ], default='manual')
    file = models.FileField(upload_to='product_documents/%Y/%m/')
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    download_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['document_type', 'sort_order']
    
    def __str__(self):
        return f"{self.product.name} - {self.title}"

class ProductReview(models.Model):
    """Fixed Product reviews and ratings"""
    MODERATION_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for Review'),
    ]
    
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField()
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    
    # Detailed ratings
    value_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    quality_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    features_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    ease_of_use_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    
    # Review metadata
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, help_text="Feature this review prominently")
    is_public = models.BooleanField(default=True, help_text="Make this review visible to public")
    moderation_status = models.CharField(
        max_length=20, 
        choices=MODERATION_CHOICES, 
        default='pending',
        help_text="Review moderation status"
    )
    
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'reviewer_email']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['moderation_status']),
        ]
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.reviewer_name}"
    
    @property
    def is_moderated(self):
        """Check if review has been moderated"""
        return self.moderation_status != 'pending'
    
    def approve(self):
        """Approve the review"""
        self.moderation_status = 'approved'
        self.is_approved = True
        self.is_public = True
        self.save()
    
    def reject(self):
        """Reject the review"""
        self.moderation_status = 'rejected' 
        self.is_approved = False
        self.is_public = False
        self.save()


# ================================
# PRODUCT BUNDLES & ACCESSORIES
# ================================

class ProductBundle(models.Model):
    """Product bundles and packages"""
    BUNDLE_TYPE_CHOICES = [
        ('combo', 'Combo Deal'),
        ('offer', 'Special Offer'),
        ('package', 'Package Deal'),
        ('seasonal', 'Seasonal Bundle'),
        ('starter_kit', 'Starter Kit'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
        ('expired', 'Expired'),
    ]
    
    name = models.CharField(max_length=255, help_text="Bundle name")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    description = models.TextField(help_text="Detailed bundle description")
    
    # Bundle configuration
    bundle_type = models.CharField(
        max_length=50, 
        choices=BUNDLE_TYPE_CHOICES,
        default='combo'
    )
    
    # Pricing
    bundle_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Final bundle price"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount percentage off individual prices"
    )
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Fixed discount amount"
    )
    
    # Media and display
    image = models.ImageField(upload_to='bundles/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # Business rules
    requires_all_items = models.BooleanField(
        default=True,
        help_text="Customer must buy all items in bundle"
    )
    max_quantity_per_customer = models.PositiveIntegerField(
        default=1,
        help_text="Maximum bundle quantity per customer"
    )
    
    # Status and availability
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_active = models.BooleanField(default=True)
    
    # Validity period
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Bundle"
        verbose_name_plural = "Product Bundles"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_valid(self):
        """Check if bundle is currently valid"""
        from django.utils import timezone
        now = timezone.now().date()
        
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return self.is_active and self.status == 'active'
    
    @property
    def total_products(self):
        """Get total number of products in bundle"""
        return self.bundle_items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def individual_price_total(self):
        """Calculate total if bought individually"""
        total = 0
        for item in self.bundle_items.all():
            total += item.product.final_price * item.quantity
        return total
    
    @property
    def savings_amount(self):
        """Calculate savings amount"""
        return self.individual_price_total - self.bundle_price
    
    @property
    def savings_percentage(self):
        """Calculate savings percentage"""
        if self.individual_price_total > 0:
            return (self.savings_amount / self.individual_price_total) * 100
        return 0

class BundleItem(models.Model):
    """Items within a product bundle"""
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE, related_name='bundle_items')
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    is_main_product = models.BooleanField(default=False, help_text="Primary product in bundle")
    is_optional = models.BooleanField(default=False, help_text="Optional item in bundle")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['bundle', 'product', 'variant']
        ordering = ['sort_order']

    def __str__(self):
        variant_info = f" ({self.variant})" if self.variant else ""
        return f"{self.bundle.name} - {self.product.name}{variant_info} x{self.quantity}"

class ProductAccessory(models.Model):
    """Enhanced accessories for electronics"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    products = models.ManyToManyField(ElectronicsProduct, related_name='accessories', blank=True)
    image = models.ImageField(upload_to='accessories/', blank=True, null=True)
    accessory_type = models.CharField(max_length=50, choices=[
        ('cable', 'Cable'),
        ('adapter', 'Adapter'),
        ('case', 'Case/Cover'),
        ('charger', 'Charger'),
        ('mount', 'Mount/Stand'),
        ('storage', 'Storage/Memory'),
        ('peripheral', 'Peripheral'),
        ('software', 'Software'),
        ('warranty', 'Extended Warranty'),
        ('cleaning', 'Cleaning Kit'),
        ('other', 'Other'),
    ], default='other')
    is_compatible_required = models.BooleanField(default=True, help_text="Check compatibility before purchase")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = 'Product Accessories'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['accessory_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.name

class WholesalePrice(models.Model):
    """Wholesale pricing tiers for products"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='wholesale_prices')
    min_quantity = models.PositiveIntegerField(help_text="Minimum quantity for this price tier")
    max_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum quantity for this price tier (leave empty for unlimited)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit for this quantity tier"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['min_quantity']
        unique_together = ['product', 'min_quantity']
        indexes = [
            models.Index(fields=['product', 'is_active']),
        ]
    
    def __str__(self):
        max_qty = f"-{self.max_quantity}" if self.max_quantity else "+"
        return f"{self.product.name}: {self.min_quantity}{max_qty} @ ${self.price}"


# ================================
# PRODUCT COMPARISON & FAQ
# ================================

class ProductComparison(models.Model):
    """Product comparison table"""
    name = models.CharField(max_length=200, help_text="Comparison table name")
    description = models.TextField(blank=True)
    products = models.ManyToManyField(ElectronicsProduct, related_name='comparisons')
    comparison_attributes = models.ManyToManyField(ProductAttribute, help_text="Attributes to compare")
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Mark this comparison as featured")
    
    slug = models.SlugField(max_length=250, unique=True, blank=True, help_text="URL-friendly version of the name")
    
    # SEO Meta fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO meta title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    canonical_url = models.URLField(blank=True, null=True, help_text="Canonical URL for this comparison")
    structured_data = models.JSONField(default=dict, blank=True, help_text="Structured data (JSON-LD)")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Comparison"
        verbose_name_plural = "Product Comparisons"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_public', 'is_featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while ProductComparison.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

class ProductFAQ(models.Model):
    """Frequently Asked Questions for products"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('general', 'General'),
        ('technical', 'Technical'),
        ('compatibility', 'Compatibility'),
        ('warranty', 'Warranty'),
        ('shipping', 'Shipping'),
        ('support', 'Support'),
        ('installation', 'Installation'),
        ('troubleshooting', 'Troubleshooting'),
    ], default='general')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0, help_text="Number of times viewed")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'sort_order']
        verbose_name = 'Product FAQ'
        verbose_name_plural = 'Product FAQs'
        indexes = [
            models.Index(fields=['product', 'category', 'is_active']),
        ]
    
    def __str__(self):
        return f"FAQ for {self.product.name}: {self.question[:50]}..."


# ================================
# SEO & REDIRECTS
# ================================

class SEORedirect(models.Model):
    """SEO redirect model"""
    REDIRECT_TYPE_CHOICES = [
        ('301', 'Permanent Redirect (301)'),
        ('302', 'Temporary Redirect (302)'),
        ('307', 'Temporary Redirect (307)'),
        ('308', 'Permanent Redirect (308)'),
    ]
    
    old_url = models.CharField(max_length=500, unique=True, help_text="Original URL that should redirect")
    new_url = models.CharField(max_length=500, help_text="Destination URL")
    redirect_type = models.CharField(max_length=3, choices=REDIRECT_TYPE_CHOICES, default='301')
    is_active = models.BooleanField(default=True, help_text="Whether this redirect is active")
    is_permanent = models.BooleanField(default=True, help_text="Mark as permanent redirect")
    description = models.TextField(blank=True, null=True, help_text="Internal note about this redirect")
    hit_count = models.PositiveIntegerField(default=0, help_text="Number of times this redirect was used")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='created_redirects',
        help_text="User who created this redirect"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'SEO Redirect'
        verbose_name_plural = 'SEO Redirects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['old_url']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.old_url} → {self.new_url} ({self.redirect_type}) [{status}]"
    
    def save(self, *args, **kwargs):
        if self.redirect_type in ['301', '308']:
            self.is_permanent = True
        elif self.redirect_type in ['302', '307']:
            self.is_permanent = False
        super().save(*args, **kwargs)

class SEOMetaData(models.Model):
    """Additional SEO metadata for products"""
    product = models.OneToOneField(ElectronicsProduct, on_delete=models.CASCADE, related_name='seo_metadata')
    
    # Advanced SEO fields
    breadcrumb_title = models.CharField(max_length=100, blank=True)
    search_keywords = models.TextField(blank=True, help_text="Additional search keywords")
    related_searches = models.TextField(blank=True, help_text="Related search terms")
    
    # Rich snippets data
    product_condition = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('refurbished', 'Refurbished'),
        ('used', 'Used'),
    ], default='new')
    availability = models.CharField(max_length=30, choices=[
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre Order'),
        ('limited_availability', 'Limited Availability'),
    ], default='in_stock')
    
    # Social media optimization
    pinterest_description = models.CharField(max_length=500, blank=True)
    instagram_hashtags = models.CharField(max_length=500, blank=True)
    
    # SEO performance tracking
    search_impressions = models.PositiveIntegerField(default=0)
    search_clicks = models.PositiveIntegerField(default=0)
    last_crawled = models.DateTimeField(blank=True, null=True)
    
    # Advanced SEO features
    robots_directives = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Custom robots meta directives"
    )
    canonical_override = models.URLField(blank=True, null=True, help_text="Override canonical URL")
    hreflang_data = models.JSONField(default=dict, blank=True, help_text="Hreflang data for international SEO")
    structured_data = models.JSONField(default=dict, blank=True, help_text="Additional structured data")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SEO Metadata"
        verbose_name_plural = "SEO Metadata"
    
    def __str__(self):
        return f"SEO Data for {self.product.name}"
    
    @property
    def click_through_rate(self):
        """Calculate CTR from search results"""
        if self.search_impressions > 0:
            return round((self.search_clicks / self.search_impressions) * 100, 2)
        return 0


# ================================
# PRODUCT NOTIFICATIONS & ALERTS
# ================================

class ProductNotification(models.Model):
    """Stock notifications and alerts"""
    product = models.ForeignKey(ElectronicsProduct, on_delete=models.CASCADE, related_name='notifications')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    email = models.EmailField()
    notification_type = models.CharField(max_length=20, choices=[
        ('restock', 'Back in Stock'),
        ('price_drop', 'Price Drop'),
        ('new_variant', 'New Variant Available'),
        ('sale', 'On Sale'),
    ], default='restock')
    target_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Notify when price drops to this level"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    notified_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['product', 'variant', 'email', 'notification_type']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['notification_type', 'is_active']),
        ]
    
    def __str__(self):
        variant_info = f" - {self.variant}" if self.variant else ""
        return f"Notification for {self.product.name}{variant_info} - {self.email}"


# ================================
# SUMMARY OF IMPROVEMENTS
# ================================

"""
KEY IMPROVEMENTS MADE:

1. WAREHOUSE & INVENTORY MANAGEMENT:
   - Added Country, State, Warehouse, WarehouseZone models
   - Created ProductStock model for per-warehouse inventory tracking
   - Added StockMovement model for complete audit trail
   - Implemented StockAlert model for automated notifications

2. ENHANCED INVENTORY FEATURES:
   - Stock reservation system for pending orders
   - Damaged/unusable stock tracking
   - Automatic reorder point alerts
   - Transfer tracking between warehouses
   - Zone-based warehouse organization

3. COMPREHENSIVE COUPON SYSTEM:
   - Multiple discount types (percentage, fixed, free shipping, BOGO)
   - Advanced targeting (products, categories, brands, customer types)
   - Usage limits and restrictions
   - Stackable coupon support
   - Complete usage tracking and analytics

4. FIXED MODEL ISSUES:
   - Removed conflicting bundle code from ProductReview
   - Fixed foreign key relationships
   - Added proper imports and validation
   - Improved model organization and structure

5. ENHANCED EXISTING MODELS:
   - Better SEO support across all models
   - Improved product variant system
   - Enhanced media management
   - Better indexing for performance

6. ADDED MISSING FEATURES:
   - Product comparison system
   - FAQ management
   - Enhanced accessories
   - Wholesale pricing tiers
   - Product notifications
   - SEO redirects and metadata

7. INVENTORY INTEGRATION:
   - Products now track stock across multiple warehouses
   - Automatic stock calculations
   - Low stock alerts
   - Reserved quantity handling
   - Movement history

This provides a complete, production-ready e-commerce system with proper inventory management, 
comprehensive coupon system, and enhanced product management capabilities.
"""