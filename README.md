# SmartScan Attendance

A two-factor authentication approach to efficient attendance taking with facial recogntion and barcode scanning.

## Background

I am currently a Sopohomore in HS, as of 2023. After noticing time wasted every class period for attendance taking, I decided to design a solution. This automated attendance taking app removes teacher intevention and allows students to quickly scan their face and ID badge to be marked present.

## Key Features

- Two-factor authentication with deep learning facial recognition and ID barcode scanning
- Automated attendance tracking for efficient time management
- User-friendly interface for both teachers and students

## Known Issues

This project is a work in progress, and there are some known issues that we are actively working to address:

1. **Unable to Detect Liveness**: Our facial recogntion model fails to detect whether the face it detects is simply an image/video or the actual person. Some potential workarounds we are considering are depth detection or training the model further.

1. **Difficulty in Differentiating Facial Features**: The current facial recognition model faces challenges in accurately distinguishing between certain facial features. We are aware that improvements are needed to ensure fairness and accuracy for all users.

## License

This project is a work in progress and is currently under active development. While we encourage contributions and feedback, please note that the project's features, structure, and licensing may evolve over time.

This project is licensed under the MIT License. See the LICENSE file for more details.
