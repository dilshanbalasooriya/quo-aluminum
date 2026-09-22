stores/toastStore.ts — Reactive store for triggering alert banners.

    components/AppToast.vue — Toast overlay visual component.

    components/ThemeToggle.vue — Dark/Light theme toggler.

    components/AppHeader.vue — Header bar.

    components/AppSidebar.vue — Collapsible role-aware menu.

    components/AppFooter.vue — Bottom bar.

    App.vue Update — Assemble header, sidebar, footer, and toasts around <RouterView/>.
_______________________________________________

1. Vue Router Routes (src/router/index.ts)

These are the named routes referenced in AppHeader.vue, AppSidebar.vue, and navigation guards:

    /login (name: 'login'): Public route for user authentication.

    /admin (name: 'admin-dashboard'): Protected route restricted to ADMIN role.

    /admin/profiles (name: 'admin-profiles'): Management page for aluminum extrusion profile prices per meter/foot.

    /admin/hardware (name: 'admin-hardware'): Management page for hardware item rates (locks, hinges, rollers, rubber seals).

    /admin/templates (name: 'admin-templates'): Template manager for window/door configurations.

    /admin/users (name: 'admin-users'): User account management (create workers, assign roles).

    /workshop/estimate (name: 'worker-dashboard'): Main workshop canvas where workers input dimensions, select templates, and calculate estimates.

    /workshop/quotes (name: 'saved-quotes'): History and status list of saved quotations.

2. TypeScript Data Interfaces (src/types/index.ts)

Strong TypeScript types ensure your frontend matches your FastAPI backend schemas:

    UserProfile: User properties (id, username, role, created_at).

    AluminumProfile: Extrusion specifications (id, code, name, weight_per_meter, price_per_kg_or_meter, finish_type).

    HardwareItem: Accessories (id, name, unit_price, category).

    WindowTemplate: Structural layout definition (id, title, type [sliding/casement/fixed], formula_rules, default_sections).

    Quotation: Complete customer estimate (id, customer_name, total_price, margin_percentage, cut_list, created_at).

3. Pinia Stores (src/stores/)

State management stores to keep UI logic clean and decoupled:

    authStore.ts: Holds active user token, user role (ADMIN vs WORKER), and login/logout methods.

    profileStore.ts: Fetches, caches, and updates aluminum profile rates from FastAPI.

    templateStore.ts: Stores window/door formulas and default configurations.

    estimationStore.ts: Holds the live calculation state (active dimensions, selected profile series, glass thickness, hardware add-ons, and cut lists).

4. Core Workshop Components (src/components/)

Components specifically needed for the estimation engine:

    FrameVisualizer.vue: Dynamic SVG/Canvas renderer that draws 2D window and door frames in real-time as workers adjust height and width.

    CutListTable.vue: Displays calculated aluminum profile lengths, miter cut angles, and material wastage.

    HardwareSelector.vue: Multi-select interface for choosing locks, handles, weather-stripping, and glass types.

    QuotePdfModal.vue: Preview and print modal for generating professional customer quotations.