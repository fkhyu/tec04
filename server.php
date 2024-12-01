<?php
header('Content-Type: application/json');

// Check if the request method is POST
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Get the raw POST data
    $data = json_decode(file_get_contents("php://input"), true);

    // Check if the data is valid
    if (isset($data['player1']['position']['x'], $data['player1']['position']['y'])) {
        // Return a success response with the received data
        echo json_encode([
            'status' => 'success',
            'message' => 'Game data received',
            'data' => $data
        ]);
    } else {
        // Return an error response if the data is missing
        echo json_encode([
            'status' => 'error',
            'message' => 'Invalid data received'
        ]);
    }
} else {
    // If the request is not POST, return an error
    echo json_encode([
        'status' => 'error',
        'message' => 'Invalid request method'
    ]);
}
?>
