-- Table for Users
CREATE TABLE users (
                       user_id INT PRIMARY KEY,
    -- Additional attributes about users can be added here
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for Action Types
CREATE TABLE action_types (
                              action_type_id INT AUTO_INCREMENT PRIMARY KEY,
                              action_type VARCHAR(255) UNIQUE NOT NULL
);

-- Table for Pages, Links, and Forms (Dimension Tables)
-- Assuming raw_str can be parsed and relevant info can be stored in these tables

-- Pages
CREATE TABLE pages (
                       page_id INT AUTO_INCREMENT PRIMARY KEY,
                       page_name VARCHAR(255) NOT NULL,
                       UNIQUE (page_name)
);

-- Links
CREATE TABLE links (
                       link_id INT AUTO_INCREMENT PRIMARY KEY,
                       link_name VARCHAR(255) NOT NULL,
                       destination_url VARCHAR(255) NOT NULL,
                       UNIQUE (link_name, destination_url)
);

-- Forms
CREATE TABLE forms (
                       form_id INT AUTO_INCREMENT PRIMARY KEY,
                       form_name VARCHAR(255) NOT NULL,
                       form_fields INT NOT NULL,
                       UNIQUE (form_name)
);

-- Fact Table for Logs
CREATE TABLE activity_logs (
                               log_id INT AUTO_INCREMENT PRIMARY KEY,
                               timestamp DATETIME NOT NULL,
                               user_id INT,
                               action_type_id INT,
                               action_count INT,
                               page_id INT DEFAULT NULL,
                               link_id INT DEFAULT NULL,
                               form_id INT DEFAULT NULL,
                               FOREIGN KEY (user_id) REFERENCES users(user_id),
                               FOREIGN KEY (action_type_id) REFERENCES action_types(action_type_id),
                               FOREIGN KEY (page_id) REFERENCES pages(page_id),
                               FOREIGN KEY (link_id) REFERENCES links(link_id),
                               FOREIGN KEY (form_id) REFERENCES forms(form_id)
);

-- You might need additional tables or columns depending on the specifics of the raw_str data and other requirements
