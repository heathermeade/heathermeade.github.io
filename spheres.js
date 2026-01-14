import * as THREE from 'three';

// Scene setup
const container = document.getElementById('three-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);

const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

// Camera position
camera.position.z = 50;

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(-10, 10, 5);
scene.add(directionalLight);

// Sphere properties
const sphereCount = 18;
const spheres = [];
const originalPositions = [];
const mouse = new THREE.Vector2();
const mouse3D = new THREE.Vector3();
const raycaster = new THREE.Raycaster();

// Create spheres
const geometry = new THREE.SphereGeometry(1, 32, 32);
const material = new THREE.MeshStandardMaterial({
  color: 0xf0f0f0,
  roughness: 0.9,
  metalness: 0.0,
});

// Initial cluster position (behind and around center)
const clusterRadius = 8;
const clusterCenter = new THREE.Vector3(0, 0, -5);

for (let i = 0; i < sphereCount; i++) {
  const sphere = new THREE.Mesh(geometry, material.clone());
  
  // Random position within cluster
  const angle = Math.random() * Math.PI * 2;
  const radius = Math.random() * clusterRadius;
  const height = (Math.random() - 0.5) * 6;
  
  sphere.position.set(
    clusterCenter.x + Math.cos(angle) * radius,
    clusterCenter.y + height,
    clusterCenter.z + Math.sin(angle) * radius
  );
  
  // Random size variation
  const scale = Math.random() * 0.5 + 0.8;
  sphere.scale.set(scale, scale, scale);
  
  // Store original position
  originalPositions.push(sphere.position.clone());
  
  // Physics properties
  sphere.userData = {
    velocity: new THREE.Vector3(0, 0, 0),
    targetPosition: sphere.position.clone(),
    originalPosition: sphere.position.clone(),
    isInteracting: false,
  };
  
  spheres.push(sphere);
  scene.add(sphere);
}

// Mouse interaction
let isMouseDown = false;

function onMouseMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  
  // Convert mouse to 3D space
  raycaster.setFromCamera(mouse, camera);
  mouse3D.copy(raycaster.ray.direction);
  mouse3D.multiplyScalar(20);
  mouse3D.add(raycaster.ray.origin);
}

function onMouseDown() {
  isMouseDown = true;
}

function onMouseUp() {
  isMouseDown = false;
}

window.addEventListener('mousemove', onMouseMove);
window.addEventListener('mousedown', onMouseDown);
window.addEventListener('mouseup', onMouseUp);

// Physics constants
const interactionRadius = 8;
const repulsionForce = 0.3;
const damping = 0.85;
const springStrength = 0.05;
const regroupSpeed = 0.02;

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  
  spheres.forEach((sphere, index) => {
    const userData = sphere.userData;
    const distanceToMouse = sphere.position.distanceTo(mouse3D);
    
    // Mouse interaction
    if (distanceToMouse < interactionRadius && isMouseDown) {
      userData.isInteracting = true;
      const direction = new THREE.Vector3()
        .subVectors(sphere.position, mouse3D)
        .normalize();
      
      const force = (interactionRadius - distanceToMouse) / interactionRadius;
      userData.velocity.add(direction.multiplyScalar(force * repulsionForce));
    } else {
      userData.isInteracting = false;
      
      // Regroup to original position
      const direction = new THREE.Vector3()
        .subVectors(originalPositions[index], sphere.position);
      
      const distance = direction.length();
      if (distance > 0.1) {
        direction.normalize();
        userData.velocity.add(direction.multiplyScalar(regroupSpeed));
      } else {
        // Apply spring force to maintain cluster
        userData.velocity.multiplyScalar(damping);
      }
    }
    
    // Apply velocity
    sphere.position.add(userData.velocity);
    
    // Apply damping
    userData.velocity.multiplyScalar(damping);
    
    // Collision detection between spheres
    spheres.forEach((otherSphere, otherIndex) => {
      if (index !== otherIndex) {
        const distance = sphere.position.distanceTo(otherSphere.position);
        const minDistance = sphere.scale.x + otherSphere.scale.x;
        
        if (distance < minDistance) {
          const direction = new THREE.Vector3()
            .subVectors(sphere.position, otherSphere.position)
            .normalize();
          
          const overlap = minDistance - distance;
          const force = overlap * 0.1;
          
          sphere.position.add(direction.multiplyScalar(force));
          userData.velocity.add(direction.multiplyScalar(force * 0.5));
        }
      }
    });
    
    // Boundary constraints
    const boundary = 25;
    if (Math.abs(sphere.position.x) > boundary) {
      sphere.position.x = Math.sign(sphere.position.x) * boundary;
      userData.velocity.x *= -0.5;
    }
    if (Math.abs(sphere.position.y) > boundary) {
      sphere.position.y = Math.sign(sphere.position.y) * boundary;
      userData.velocity.y *= -0.5;
    }
    if (sphere.position.z > 10 || sphere.position.z < -20) {
      sphere.position.z = Math.max(-20, Math.min(10, sphere.position.z));
      userData.velocity.z *= -0.5;
    }
  });
  
  renderer.render(scene, camera);
}

// Handle window resize
function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener('resize', onWindowResize);

// Start animation
animate();
