import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
} from 'react'

import {
  ArcRotateCamera,
  Color3,
  Color4,
  Engine,
  HemisphericLight,
  MeshBuilder,
  PointLight,
  Scene,
  StandardMaterial,
  Vector3,
} from '@babylonjs/core'

function createMaterial(scene, name, color, alpha = 1) {
  const material = new StandardMaterial(name, scene)

  material.diffuseColor = Color3.FromHexString(color)
  material.specularColor = new Color3(0.15, 0.15, 0.15)
  material.alpha = alpha

  return material
}

function createChair(scene, position, rotationY, material) {
  const chairMaterial = material.clone(
    `${material.name}-${position.x}-${position.z}`
  )

  chairMaterial.emissiveColor = new Color3(0, 0, 0)

  const seat = MeshBuilder.CreateBox(
    'chair-seat',
    {
      width: 1.4,
      depth: 1.4,
      height: 0.25,
    },
    scene
  )

  seat.position = position
  seat.rotation.y = rotationY
  seat.material = chairMaterial

  const back = MeshBuilder.CreateBox(
    'chair-back',
    {
      width: 1.4,
      depth: 0.25,
      height: 2,
    },
    scene
  )

  back.position = new Vector3(
    position.x - Math.sin(rotationY) * 0.6,
    position.y + 1,
    position.z - Math.cos(rotationY) * 0.6
  )

  back.rotation.y = rotationY
  back.material = chairMaterial

  return {
    seat,
    back,
    material: chairMaterial,
    position,
  }
}

function createBoardroom(scene) {
  const floorMaterial = createMaterial(
    scene,
    'floor-material',
    '#0b0e12'
  )

  const wallMaterial = createMaterial(
    scene,
    'wall-material',
    '#10161d'
  )

  const tableMaterial = createMaterial(
    scene,
    'table-material',
    '#1a2028'
  )

  const chairMaterial = createMaterial(
    scene,
    'chair-material',
    '#202832'
  )

  const accentMaterial = createMaterial(
    scene,
    'accent-material',
    '#080d12'
  )

  // FLOOR
  const floor = MeshBuilder.CreateGround(
    'boardroom-floor',
    {
      width: 24,
      height: 18,
    },
    scene
  )

  floor.material = floorMaterial

  // BACK WALL
  const backWall = MeshBuilder.CreateBox(
    'back-wall',
    {
      width: 24,
      height: 9,
      depth: 0.3,
    },
    scene
  )

  backWall.position = new Vector3(0, 4.5, 5)
  backWall.material = wallMaterial

  // LEFT WALL
  const leftWall = MeshBuilder.CreateBox(
    'left-wall',
    {
      width: 0.3,
      height: 9,
      depth: 18,
    },
    scene
  )

  leftWall.position = new Vector3(-12, 4.5, 0)
  leftWall.material = wallMaterial

  // RIGHT WALL
  const rightWall = MeshBuilder.CreateBox(
    'right-wall',
    {
      width: 0.3,
      height: 9,
      depth: 18,
    },
    scene
  )

  rightWall.position = new Vector3(12, 4.5, 0)
  rightWall.material = wallMaterial

  // TABLE
  const table = MeshBuilder.CreateBox(
    'conference-table',
    {
      width: 8,
      depth: 4,
      height: 0.55,
    },
    scene
  )

  table.position = new Vector3(0, 1.25, 0)
  table.material = tableMaterial

  // TABLE BASE
  const tableBase = MeshBuilder.CreateBox(
    'table-base',
    {
      width: 5,
      depth: 2,
      height: 1.2,
    },
    scene
  )

  tableBase.position = new Vector3(0, 0.6, 0)
  tableBase.material = tableMaterial

  // NOVA DISPLAY
  const display = MeshBuilder.CreateBox(
    'nova-display',
    {
      width: 7,
      height: 3,
      depth: 0.2,
    },
    scene
  )

  display.position = new Vector3(0, 4.5, 4.75)
  display.material = accentMaterial

  // AGENTS
  const agents = {
    ceo: createChair(
      scene,
      new Vector3(0, 1, -4),
      0,
      chairMaterial
    ),

    marketing: createChair(
      scene,
      new Vector3(-5, 1, 0),
      Math.PI / 2,
      chairMaterial
    ),

    sales: createChair(
      scene,
      new Vector3(5, 1, 0),
      -Math.PI / 2,
      chairMaterial
    ),

    finance: createChair(
      scene,
      new Vector3(-3.5, 1, 3),
      Math.PI,
      chairMaterial
    ),

    inventory: createChair(
      scene,
      new Vector3(3.5, 1, 3),
      Math.PI,
      chairMaterial
    ),
  }

  return agents
}

const BoardroomScene = forwardRef(function BoardroomScene(
  { activeAgent = null },
  ref
) {
  const canvasRef = useRef(null)
  const sceneRef = useRef(null)
  const cameraRef = useRef(null)
  const agentsRef = useRef(null)

  useImperativeHandle(ref, () => ({
    focusAgent(agent) {
      focusCamera(agent)
    },
  }))

  function focusCamera(agent) {
    const camera = cameraRef.current
    const agents = agentsRef.current

    if (!camera || !agents || !agents[agent]) {
      return
    }

    const target = agents[agent].position

    const newTarget = new Vector3(
      target.x,
      1.5,
      target.z
    )

    const directionX = target.x

    let targetAlpha = -Math.PI / 2

    if (directionX < -1) {
      targetAlpha = -Math.PI / 2 - 0.12
    }

    if (directionX > 1) {
      targetAlpha = -Math.PI / 2 + 0.12
    }

    const startTarget = camera.target.clone()
    const startAlpha = camera.alpha
    const startRadius = camera.radius

    const duration = 45

    let frame = 0

    const animate = () => {
      frame += 1

      const progress = Math.min(frame / duration, 1)

      // Smooth ease-in-out
      const eased =
        progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2

      camera.target = Vector3.Lerp(
        startTarget,
        newTarget,
        eased
      )

      camera.alpha =
        startAlpha +
        (targetAlpha - startAlpha) * eased

      camera.radius =
        startRadius +
        (15.5 - startRadius) * eased

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    animate()
  }

  useEffect(() => {
    const canvas = canvasRef.current

    if (!canvas) {
      return
    }

    const engine = new Engine(canvas, true)
    const scene = new Scene(engine)

    sceneRef.current = scene

    scene.clearColor = new Color4(
      0.015,
      0.02,
      0.025,
      1
    )

    // CAMERA
    const camera = new ArcRotateCamera(
      'boardroom-camera',
      -Math.PI / 2,
      Math.PI / 2.25,
      17,
      new Vector3(0, 1.5, 0),
      scene
    )

    camera.lowerAlphaLimit =
      -Math.PI / 2 - 0.35

    camera.upperAlphaLimit =
      -Math.PI / 2 + 0.35

    camera.lowerBetaLimit = Math.PI / 2.5
    camera.upperBetaLimit = Math.PI / 2.05

    camera.lowerRadiusLimit = 14
    camera.upperRadiusLimit = 19

    camera.wheelPrecision = 100
    camera.panningSensibility = 0

    camera.attachControl(canvas, true)

    cameraRef.current = camera

    // LIGHTING
    const ambientLight = new HemisphericLight(
      'ambient-light',
      new Vector3(0, 1, 0),
      scene
    )

    ambientLight.intensity = 0.65

    const mainLight = new PointLight(
      'main-light',
      new Vector3(-5, 7, -4),
      scene
    )

    mainLight.intensity = 5
    mainLight.range = 20

    const rimLight = new PointLight(
      'rim-light',
      new Vector3(0, 5, 4),
      scene
    )

    rimLight.intensity = 1.2
    rimLight.range = 12

    // ROOM
    agentsRef.current = createBoardroom(scene)

    engine.runRenderLoop(() => {
      scene.render()
    })

    const handleResize = () => {
      engine.resize()
    }

    window.addEventListener(
      'resize',
      handleResize
    )

    return () => {
      window.removeEventListener(
        'resize',
        handleResize
      )

      scene.dispose()
      engine.dispose()
    }
  }, [])

  // ACTIVE AGENT
  useEffect(() => {
    const agents = agentsRef.current

    if (!agents) {
      return
    }

    Object.entries(agents).forEach(
      ([name, agent]) => {
        const isActive = name === activeAgent

        agent.material.emissiveColor =
          isActive
            ? Color3.FromHexString('#1d6b52')
            : new Color3(0, 0, 0)
      }
    )

    if (activeAgent) {
      focusCamera(activeAgent)
    }
  }, [activeAgent])

  return (
    <canvas
      ref={canvasRef}
      className="boardroom-canvas"
    />
  )
})

export default BoardroomScene