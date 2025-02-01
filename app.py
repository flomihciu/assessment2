<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script>
        // Update this line to use the public EC2 IP address for your backend
        const API_URL = 'http://3.217.28.40:8000';  // Update with EC2 public IP address

        // Fetch and display all users
        function fetchUsers() {
            $.getJSON(API_URL + '/users', function(data) {
                const users = data.users;
                let output = `
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Age</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                users.forEach(user => {
                    output += `
                        <tr>
                            <td>${user.user_id}</td>
                            <td>${user.name}</td>
                            <td>${user.email}</td>
                            <td>${user.age || 'N/A'}</td>
                            <td>
                                <button class="btn btn-primary btn-sm edit-btn" data-id="${user.user_id}" data-toggle="modal" data-target="#editUserModal">Edit</button>
                                <button class="btn btn-danger btn-sm delete-btn" data-id="${user.user_id}">Delete</button>
                            </td>
                        </tr>
                    `;
                });
                output += '</tbody></table>';
                $('#userList').html(output);

                // Attach event handlers for edit and delete buttons
                $('.edit-btn').click(showEditUserModal);
                $('.delete-btn').click(deleteUser);
            });
        }

        // Add a new user
        function addUser() {
            const name = $('#addName').val();
            const email = $('#addEmail').val();
            const age = $('#addAge').val();
            $.ajax({
                url: API_URL + '/users',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ name, email, age }),
                success: function() {
                    $('#addUserForm')[0].reset();
                    fetchUsers();  // Reload the user list after adding
                }
            });
        }

        // Show the edit user modal with pre-filled data
        function showEditUserModal() {
            const userId = $(this).data('id');
            $.getJSON(API_URL + `/users/${userId}`, function(data) {
                $('#editUserId').val(data.user.user_id);
                $('#editName').val(data.user.name);
                $('#editEmail').val(data.user.email);
                $('#editAge').val(data.user.age);
            });
        }

        // Edit an existing user
        function editUser() {
            const userId = $('#editUserId').val();
            const name = $('#editName').val();
            const email = $('#editEmail').val();
            const age = $('#editAge').val();
            $.ajax({
                url: API_URL + `/users/${userId}`,
                type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({ name, email, age }),
                success: function() {
                    $('#editUserModal').modal('hide');
                    fetchUsers();  // Reload the user list after updating
                }
            });
        }

        // Delete a user
        function deleteUser() {
            const userId = $(this).data('id');
            $.ajax({
                url: API_URL + `/users/${userId}`,
                type: 'DELETE',
                success: function() {
                    fetchUsers();  // Reload the user list after deletion
                }
            });
        }

        // Initialize the page
        $(document).ready(function() {
            fetchUsers();
            $('#addUserForm').submit(function(e) {
                e.preventDefault();
                addUser();
            });
            $('#editUserForm').submit(function(e) {
                e.preventDefault();
                editUser();
            });
        });
    </script>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">User Management</h1>
        <div id="userList" class="mt-4"></div>

        <!-- Add User Form -->
        <h2>Add User</h2>
        <form id="addUserForm" class="form-inline">
            <input type="text" id="addName" class="form-control mr-2" placeholder="Name" required>
            <input type="email" id="addEmail" class="form-control mr-2" placeholder="Email" required>
            <input type="number" id="addAge" class="form-control mr-2" placeholder="Age">
            <button type="submit" class="btn btn-success">Add User</button>
        </form>

        <!-- Edit User Modal -->
        <div class="modal fade" id="editUserModal" tabindex="-1" role="dialog" aria-labelledby="editUserModalLabel" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="editUserModalLabel">Edit User</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="editUserForm">
                            <input type="hidden" id="editUserId">
                            <div class="form-group">
                                <label for="editName">Name</label>
                                <input type="text" id="editName" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="editEmail">Email</label>
                                <input type="email" id="editEmail" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="editAge">Age</label>
                                <input type="number" id="editAge" class="form-control">
                            </div>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>

