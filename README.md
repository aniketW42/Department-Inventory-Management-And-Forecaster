# Department Inventory Management and Forecaster

The **Department Inventory Management and Forecaster** is a web-based application designed to streamline inventory management within a department. It provides role-based access for users (Clerk, Faculty, HOD) to perform specific actions and includes features for forecasting inventory usage, generating reports, and managing item requests.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Django](https://img.shields.io/badge/Django-4.x-green) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-blueviolet)

---

## Key Features

### 1. Role-Based Access Control
- **Clerk**:
  - Add, edit, and delete inventory items.
  - Manage item requests (approve, reject, issue items).
  - View inventory statistics (e.g., low stock, out-of-stock).
- **Faculty**:
  - Request items from the inventory.
  - View the status of their requests.
- **HOD (Head of Department)**:
  - Approve or reject faculty item requests.
  - View detailed reports and inventory usage statistics.

### 2. Inventory Management
- Add items with details: name, description, category, quantity, reorder level.
- Edit or delete existing items.
- Categorize items (e.g., Furniture, Electronics, Stationery, Tools).
- Track stock levels and identify low-stock or out-of-stock items.

### 3. Item Requests
- Faculty can submit item requests with quantity and reason.
- HODs approve or reject requests, with notifications sent to requesters.
- Clerks issue approved items and update the system.

### 4. Notifications
- Alerts for request approvals, rejections, or low stock.
- Displayed in a dedicated notification center.

### 5. Reports and Forecasting
- Generate reports on inventory usage and request history.
- Forecast future inventory needs using Holt-Winters Exponential Smoothing (via Statsmodels).
- Export reports as Excel or PDF.

### 6. User-Friendly Interface
- Intuitive, responsive design with Bootstrap.
- Dynamic navigation bar with active link highlighting.
- Role-specific dashboards for Clerks, Faculty, and HODs.

---

## Technologies Used

### Backend
- **Django**: Python web framework for rapid development.
- **SQLite**: Default database (supports PostgreSQL/MySQL in production).

### Frontend
- **HTML5, CSS3, JavaScript**: Core UI technologies.
- **Bootstrap**: Responsive, modern UI components.
- **Chart.js**: Data visualization for inventory stats.

### Libraries and Tools
- **Statsmodels**: Inventory usage forecasting.
- **OpenPyXL**: Excel file handling.
- **FontAwesome & Bootstrap Icons**: Visual enhancements.

---
### Contact
For questions or suggestions:

#### **Name**: Aniket Wakte
- **Email**: [aniketwakte42@gmail.com](aniketwakte42@gmail.com)
- **GitHub**: [aniketW42](https://github.com/aniketW42/)

#### **Name**: Rohit Ray
- **Email**: [rayrohit999@gmail.com](rayrohit999@gmail.com)
- **GitHub**: [rayrohit999](https://github.com/rayrohit999)
