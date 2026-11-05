CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    phone_number VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_category VARCHAR(100),
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price BIGINT NOT NULL,
    photo_path TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    wp_post_id INTEGER,
    channel_msg_id BIGINT,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);