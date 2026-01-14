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
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Camera position
camera.position.z = 20;

// Lighting
const hemi = new THREE.HemisphereLight(
  0xb7c7ff, // cool blue sky
  0xf2b7c6, // warm pink ground
  0.85
);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xdbe6ff, 0.9);
key.position.set(-10, 12, 10);
scene.add(key);
const fill = new THREE.DirectionalLight(0xffd6c9, 0.35);
fill.position.set(10, -6, 12);
scene.add(fill);

// Sphere properties
const sphereCount = 17;
const spheres = [];
const originalPositions = [];
const mouse = new THREE.Vector2();
const raycaster = new THREE.Raycaster();
// Interaction plane at cluster depth (z = -5)
const interactionPlane = new THREE.Plane(
  new THREE.Vector3(0, 0, 1),
  -2
);
const hitPoint = new THREE.Vector3();
let hasHitPoint = false;
let isMouseDown = false;

// Create spheres
const geometry = new THREE.SphereGeometry(1.7, 64, 64);
const material = new THREE.MeshStandardMaterial({
  color: 0xf7f7fb,
  roughness: 0.75,
  metalness: 0.0,
});
material.transparent = false;
material.opacity = 1;
material.depthTest = true;
material.depthWrite = true;

// Initial cluster position (behind and around center)
const clusterRadius = 9;
const clusterCenter = new THREE.Vector3(0, 0.5, 2);

for (let i = 0; i < sphereCount; i++) {
  const sphere = new THREE.Mesh(geometry, material.clone());
  
  // Random position within cluster
  const angle = Math.random() * Math.PI * 2;
  const radius = Math.random() * clusterRadius;
  const height = (Math.random() - 0.5) * 5;
  
  sphere.position.set(
    clusterCenter.x + Math.cos(angle) * radius,
    clusterCenter.y + height,
    clusterCenter.z + Math.sin(angle) * radius
  );
  
  // Random size variation
  const scale = Math.random() * 0.6 + 0.7;
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

function onMouseMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);

  hasHitPoint =
    raycaster.ray.intersectPlane(interactionPlane, hitPoint) !== null;
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
const interactionRadius = 12;
const repulsionStrength = 0.9;
const damping = 0.88;
const returnStrength = 0.03;

// Animation loop
function animate() {
  requestAnimationFrame(animate);

  spheres.forEach((sphere, index) => {
    const userData = sphere.userData;

    // 1. Mouse interaction (repulsion)
    if (hasHitPoint) {
      const toSphere = new THREE.Vector3()
        .subVectors(sphere.position, hitPoint);
      const d = toSphere.length();

      if (d < interactionRadius) {
        const t = 1 - d / interactionRadius;
        const force = t * t * repulsionStrength;

        toSphere.normalize();
        userData.velocity.add(toSphere.multiplyScalar(force));
      }
    }

    // 2. Spring back to original position
    const back = new THREE.Vector3()
      .subVectors(originalPositions[index], sphere.position);
    userData.velocity.add(back.multiplyScalar(returnStrength));

    // 3. Apply velocity
    sphere.position.add(userData.velocity);

    // 4. Apply damping
    userData.velocity.multiplyScalar(damping);

    // 5. HARD SPHERE COLLISIONS (no melting)
    for (let j = index + 1; j < spheres.length; j++) {
      const a = sphere;
      const b = spheres[j];

      const delta = new THREE.Vector3().subVectors(b.position, a.position);
      const dist = delta.length();

      const ra = a.scale.x * 1.7; // must match SphereGeometry radius
      const rb = b.scale.x * 1.7;

      const minDist = ra + rb;

      if (dist > 0.0001 && dist < minDist) {
        const overlap = minDist - dist;

        delta.multiplyScalar(1 / dist);
        const correction = delta.multiplyScalar(overlap * 0.5);

        a.position.addScaledVector(correction, -1);
        b.position.addScaledVector(correction,  1);

        a.userData.velocity.addScaledVector(correction, -0.05);
        b.userData.velocity.addScaledVector(correction,  0.05);
      }
    }

    // 6. Boundary constraints (THIS GOES HERE 👇)
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
