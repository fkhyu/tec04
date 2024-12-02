<?php
// server.php

// Allow cross-origin requests
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

// File to store the data (simple persistence for demo purposes)
$filename = 'shared_data.json';

// Check if the request method is POST (to save data)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the posted data
    $data = json_decode(file_get_contents('php://input'), true);

    if ($data && isset($data['client_id']) && isset($data['message'])) {
        // Read existing data from the file
        $stored_data = [];
        if (file_exists($filename)) {
            $stored_data = json_decode(file_get_contents($filename), true);
        }

        // Save the new data under the corresponding client_id
        $stored_data[$data['client_id']] = $data['message'];
        $stored_data['speed'] = 100;
        $stored_data['radius'] = 20;
        $stored_data['a'] = 1.00001;
        $stored_data['max_fps'] = 60;
        $stored_data['boost_count'] = 70;
        $stored_data['world_size'] = 800;

        // Write the updated data back to the file
        file_put_contents($filename, json_encode($stored_data));

        echo json_encode(['status' => 'success', 'message' => 'Data saved']);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Invalid data']);
    }
} 
// Check if the request method is GET (to retrieve data)
elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (isset($_GET['client_id'])) {
        // Get client_id to avoid returning own data
        $client_id = $_GET['client_id'];

        // Read the data from the file
        if (file_exists($filename)) {
            $stored_data = json_decode(file_get_contents($filename), true);

            // Remove the client's own data
            unset($stored_data[$client_id]);

            // Return the remaining data (data from other clients)
            if (!empty($stored_data)) {
                echo json_encode($stored_data);
            } else {
                echo json_encode(['status' => 'error', 'message' => 'No other data found']);
            }
        } else {
            echo json_encode(['status' => 'error', 'message' => 'No data found']);
        }
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Client ID is required']);
    }
} else {
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method']);
}
?>
