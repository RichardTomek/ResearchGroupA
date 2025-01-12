// --------------
// SETTINGS
// --------------

// Size of the Game Window
let game_width = 900;
let game_height = 600;
let game_background_color = "#dcdcdc"
let score_per_ball = 100

let n_lanes = 4;                        // Number of lanes ball can spawn in
let show_lane_border = true;

let n_balls = 10;                        // Number of balls in the game (they will "respawn)
let ball_speed = 1;                     // Downwards speed in px/frame
let ball_acceleration = 1.01;
let ball_color = "#f6cd00"
let ball_border_color = "#a09042"
let ball_size = 0.4                    // Percent of lane width
let ball_spawn_interval = 750           // Time between ball spawns in ms

let paddle_width = .8;                  // Percent of lane width
let paddle_height = 10;                 // Height of the paddle in px
let paddle_y_offset = 20;               // Distance from the bottom of the canvas in px
let paddle_color = "#006f00"
let paddble_border_color = "#000000"


// --------------
// GLOBAL VARIABLES
// --------------
// Do not change anything here. These are auto populated

let lane_width = game_width / n_lanes;
let paddle = new Paddle(
    lane_width * paddle_width,
    paddle_height,
    paddle_y_offset,
    paddle_color,
    paddble_border_color,
    lane_width,
    game_width,
    game_height,
    n_lanes
)

// Generate the correct number of balls
let balls = []
for (let i = 0; i < n_balls; i++) {
    balls.push(new Ball(
        ball_speed,
        ball_acceleration,
        lane_width * ball_size,
        ball_color,
        ball_border_color,
        lane_width,
        n_lanes,
        game_height,
        false,
        true
    ))
}

// Used to determine if a new ball can already be spawned
let last_ball_spawn = 0;

let score = 0;

// --------------
// HELPER FUNCTIONS
// --------------

function random_int(max) {
    return Math.floor(Math.random() * max);
}

function spawn_ball(balls) {
    // Find if we have a ball available that is not currently active
    let ball = null;
    for (const potential_ball of balls) {
        if (!potential_ball.is_active()) {
            ball = potential_ball
        }
    }

    if (ball) {
        // We found a free ball. Generate random lane
        let lane = random_int(n_lanes);
        console.log("Spaning in lane " + lane)
        ball.spawn_in_lane(lane);

        // set the global ball spawn timer
        last_ball_spawn = Date.now();
    } else {
        console.log("No ball available to spawn");
    }
}


function checkCollision(ball, paddle) {
    // Only check collision if ball is in the same lane as paddle
    if (ball.lane !== paddle.current_lane || !ball.is_active()) {
        return false;
    }

    // Get ball's bottom edge Y position
    let ballBottomEdge = ball.get_lower_edge();

    // Get paddle's vertical range
    let paddleTop = paddle.get_upper_edge();
    let paddleBottom = paddle.get_lower_edge();

    // Ball is caught if its bottom edge touches or enters the paddle's vertical range
    // but hasn't gone completely through the paddle
    return ballBottomEdge >= paddleTop && ballBottomEdge <= paddleBottom;
}

// --------------
// RENDERING
// --------------

// p5.js setup function - runs once at the start
function setup() {
    // Create canvas with defined dimensions and parent it to our container
    let canvas = createCanvas(game_width, game_height);
    canvas.parent('canvas-container');
}

// p5.js draw function - runs continuously
function draw() {
    background(220);

    if (Date.now() - last_ball_spawn >= ball_spawn_interval) {
        spawn_ball(balls);
    }

    for (const ball of balls) {
        ball.render();

        if (checkCollision(ball, paddle)) {
            ball.set_active(false);
            score += score_per_ball;
        }
    }

    paddle.render();

    // Optional: Display score on canvas
    fill(0);
    noStroke();
    textSize(20);
    text('Score: ' + score, 10, 30);
}