import { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { Text3D, Center, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { MotionValue } from 'framer-motion';
import { TTFLoader } from 'three/examples/jsm/loaders/TTFLoader.js';

const GlassLetter = ({ char, xOffset, scrollY }: { char: string, xOffset: number, scrollY: MotionValue<number> }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const fontData = useLoader(TTFLoader, '/fonts/Aquire-Bold.otf');
  
  // Random trajectory constants for "deconstruction"
  const trajectory = useMemo(() => ({
    x: (Math.random() - 0.5) * 60,
    y: (Math.random() - 0.5) * 60,
    z: (Math.random() - 0.5) * 100,
    rotX: (Math.random() - 0.5) * 10,
    rotY: (Math.random() - 0.5) * 10,
    rotZ: (Math.random() - 0.5) * 10,
  }), []);

  useFrame(() => {
    if (meshRef.current) {
      // scrollY goes from 0 (top) to 1 (bottom of the whole site)
      // We want the deconstruction to happen just as they scroll down.
      const rawProgress = scrollY.get();
      const progress = Math.min(Math.max(rawProgress * 2.5, 0), 1); 
      
      // Easing function for explosion
      const ease = progress * progress * (3 - 2 * progress); 
      
      meshRef.current.position.x = xOffset + trajectory.x * ease;
      meshRef.current.position.y = trajectory.y * ease;
      meshRef.current.position.z = trajectory.z * ease;
      
      meshRef.current.rotation.x = trajectory.rotX * ease;
      meshRef.current.rotation.y = trajectory.rotY * ease;
      meshRef.current.rotation.z = trajectory.rotZ * ease;
    }
  });

  return (
    <Text3D
      ref={meshRef}
      position={[xOffset, 0, 0]}
      font={fontData as any}
      size={5}
      height={0.4}
      curveSegments={12}
      bevelEnabled
      bevelThickness={0.05}
      bevelSize={0.05}
      bevelOffset={0}
      bevelSegments={5}
    >
      {char}
      <meshPhysicalMaterial 
        color="#1e3a29"
        transparent={true}
        opacity={0.45}
        roughness={0.1}
        metalness={0.4}
        clearcoat={1}
        clearcoatRoughness={0.1}
        ior={1.5} 
        envMapIntensity={2.5}
        side={THREE.DoubleSide}
      />
    </Text3D>
  );
};

const DeconstructingText = ({ scrollY }: { scrollY: MotionValue<number> }) => {
  // Bold layout for "UPCYCLE AI" mapped linearly for size 5.0
  const letters = [
    { char: 'U', x: 0 },
    { char: 'P', x: 4.8 },
    { char: 'C', x: 9.7 },
    { char: 'Y', x: 14.6 },
    { char: 'C', x: 19.4 },
    { char: 'L', x: 24.3 },
    { char: 'E', x: 28.3 },
    { char: 'A', x: 35.0 },
    { char: 'I', x: 40.7 },
  ];

  return (
    <Center>
      <group>
        {letters.map((val, idx) => (
          <GlassLetter key={idx} char={val.char} xOffset={val.x} scrollY={scrollY} />
        ))}
      </group>
    </Center>
  );
};

export const HeroTitle3D = ({ scrollY }: { scrollY: MotionValue<number> }) => {
  return (
    <div className="w-full h-[350px] md:h-[500px] lg:h-[600px] relative z-20 pointer-events-none mb-0">
      <Canvas camera={{ position: [0, 0, 58], fov: 35 }}>
        <Environment preset="city" />
        <ambientLight intensity={0.8} />
        <directionalLight position={[10, 10, 10]} intensity={1.5} />
        <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
        
        <Suspense fallback={null}>
          <DeconstructingText scrollY={scrollY} />
        </Suspense>
      </Canvas>
    </div>
  );
};
