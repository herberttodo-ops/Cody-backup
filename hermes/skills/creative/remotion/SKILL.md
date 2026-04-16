---
name: remotion
title: Remotion
version: 1.0.0
category: creative
tags: [video, react, rendering, automation, motion-graphics]
description: |
  Create programmatic videos with React and TypeScript using Remotion.
  Covers project setup, composition authoring, rendering pipelines (local/Lambda),
  data-driven videos, and production workflows.
---

# Remotion

Create videos programmatically using React components. Render to MP4, GIF, or image sequences.

## Quick Start

### 1. Initialize a New Project

```bash
# Using npm
npm create remotion@latest

# Using pnpm
pnpm create remotion@latest

# Using yarn
yarn create remotion

# Using bun
bun create remotion@latest
```

Select a template during setup:
- `Hello World` - Basic starter
- `Blank` - Minimal setup
- `Three.js` - 3D graphics
- `Still` - Image generation only
- `Tailwind` - With Tailwind CSS
- `Transparent Video` - Alpha channel support

### 2. Project Structure

```
my-remotion-project/
├── src/
│   ├── Root.tsx          # Entry point, all compositions defined here
│   ├── HelloWorld/       # Composition components
│   │   ├── index.tsx
│   │   └── styles.css
│   ├── my-video/
│   │   └── index.tsx
│   └── video.ts          # Constants (fps, duration, dimensions)
├── public/               # Static assets (images, fonts, audio)
├── remotion.config.ts    # Remotion configuration
├── package.json
└── tsconfig.json
```

### 3. Start Preview Server

```bash
npm run dev          # Start preview at http://localhost:3000
```

## Core Concepts

### Composition

The basic unit of a Remotion video:

```tsx
// src/Root.tsx
import {Composition} from 'remotion';
import {MyVideo} from './MyVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={150}      // 5 seconds at 30fps
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        titleText: 'Hello World',
        titleColor: 'black',
      }}
    />
  );
};
```

### Component with useCurrentFrame

```tsx
// src/MyVideo.tsx
import {useCurrentFrame, useVideoConfig} from 'remotion';

export const MyVideo: React.FC<{
  titleText: string;
  titleColor: string;
}> = ({titleText, titleColor}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, fps} = useVideoConfig();

  // Fade in from frame 0-30
  const opacity = Math.min(1, frame / 30);

  return (
    <div style={{opacity, color: titleColor}}>
      <h1>{titleText}</h1>
      <p>Frame: {frame} / {durationInFrames}</p>
    </div>
  );
};
```

## Animation Utilities

### spring() for Natural Motion

```tsx
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

const frame = useCurrentFrame();
const {fps} = useVideoConfig();

const scale = spring({
  fps,
  frame,
  config: {
    damping: 200,
    stiffness: 100,
    mass: 0.5,
  },
  from: 0,
  to: 1,
  durationInFrames: 30,
});

// Use in style
<div style={{transform: `scale(${scale})`}} />
```

### interpolate() for Range Mapping

```tsx
import {interpolate, useCurrentFrame} from 'remotion';

const frame = useCurrentFrame();

// Fade in during frames 0-30, fade out 120-150
const opacity = interpolate(
  frame,
  [0, 30, 120, 150],
  [0, 1, 1, 0]
);

// Easing
import {Easing} from 'remotion';
const value = interpolate(frame, [0, 100], [0, 1], {
  easing: Easing.bezier(0.8, 0.22, 0.15, 0.85),
});
```

### interpolateColors()

```tsx
import {interpolateColors, useCurrentFrame} from 'remotion';

const frame = useCurrentFrame();

const backgroundColor = interpolateColors(
  frame,
  [0, 100],
  ['#ff0000', '#0000ff']
);
```

## Sequences

Compose multiple scenes in series:

```tsx
import {Sequence} from 'remotion';

export const Video: React.FC = () => {
  return (
    <>
      <Sequence from={0} durationInFrames={150}>
        <IntroScene />
      </Sequence>
      <Sequence from={150} durationInFrames={300}>
        <MainContent />
      </Sequence>
      <Sequence from={450} durationInFrames={90}>
        <OutroScene />
      </Sequence>
    </>
  );
};
```

With layout="absolute-fill" (default positioning):

```tsx
<Sequence layout="absolute-fill" from={0} durationInFrames={150}>
  <Scene />
</Sequence>
```

## Data and Input Props

### Define Props Interface

```tsx
// src/MyVideo.tsx
import {z} from 'zod';
import {zColor} from '@remotion/zod-types';

export const myVideoSchema = z.object({
  titleText: z.string(),
  titleColor: zColor(),
  logoUrl: z.string().url(),
  duration: z.number().default(5),
});

export type MyVideoProps = z.infer<typeof myVideoSchema>;

export const MyVideo: React.FC<MyVideoProps> = (props) => {
  // Component implementation
};
```

### Configure with calculateMetadata

```tsx
// src/Root.tsx
import {calculateMetadata, Composition} from 'remotion';
import {MyVideo, myVideoSchema} from './MyVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MyVideo"
      component={MyVideo}
      calculateMetadata={({props}) => {
        return {
          props,
          durationInFrames: props.duration * 30,
          fps: 30,
          width: 1920,
          height: 1080,
        };
      }}
      schema={myVideoSchema}
      defaultProps={{
        titleText: 'Hello World',
        titleColor: '#000000',
        logoUrl: 'https://example.com/logo.png',
        duration: 5,
      }}
    />
  );
};
```

### Pass Props via Render Command

```bash
npx remotion render src/index.ts MyVideo --props='{"titleText":"Custom Title"}'

# Or from file
npx remotion render src/index.ts MyVideo --props=./input.json
```

## Rendering

### Local Rendering

```bash
# Basic render
npx remotion render src/index.ts MyVideo

# With custom output
npx remotion render src/index.ts MyVideo out/video.mp4

# Image sequence (for post-production)
npx remotion render src/index.ts MyVideo out/frame-%04d.png --codec=png

# GIF
npx remotion render src/index.ts MyVideo out/anim.gif --codec=gif

# Still frame (image)
npx remotion still src/index.ts MyVideo --frame=30 out/frame.png
```

### Render Options

```bash
# Quality settings
npx remotion render src/index.ts MyVideo --quality=100 --crf=18

# Concurrent frames (faster but more memory)
npx remotion render src/index.ts MyVideo --concurrency=4

# Scale for faster preview renders
npx remotion render src/index.ts MyVideo --scale=0.5

# Log level
npx remotion render src/index.ts MyVideo --log=verbose

# Bundle only (for Lambda)
npx remotion bundle src/index.ts
```

### Lambda Rendering (Cloud)

```bash
# Install Lambda package
npm install @remotion/lambda

# Setup (once per AWS account)
npx remotion lambda policies validate
npx remotion lambda functions deploy

# Render on Lambda
npx remotion lambda render "s3://my-bucket" src/index.ts MyVideo \
  --privacy=public \
  --props='{"titleText":"Cloud Rendered"}'
```

## Static Assets

### Images

```tsx
import {Img, staticFile} from 'remotion';

// From public folder
<Img src={staticFile('logo.png')} />

// Remote URL (allowlisted in remotion.config.ts)
<Img src="https://example.com/image.jpg" />

// With fallback
import {useImage} from 'remotion';
const {img, error} = useImage(src);
```

### Audio

```tsx
import {Audio} from 'remotion';

<Audio src={staticFile('background-music.mp3')} />

// Start at specific time, control volume
<Audio
  src={staticFile('voiceover.mp3')}
  startFrom={30}
  endAt={300}
  volume={0.8}
/>
```

### Video

```tsx
import {Video} from 'remotion';

<Video src={staticFile('background.mp4')} />

// With playback rate (2x speed = half duration)
<Video src={staticFile('clip.mp4')} playbackRate={2} />
```

## Configuration

### remotion.config.ts

```ts
import {Config} from '@remotion/cli/config';

// Output directory
Config.setOutputLocation('out/render.mp4');

// Allow remote URLs
Config.setAllowedImageOrigins(['https://example.com']);

// Puppeteer settings
Config.setChromiumHeadlessMode(true);
Config.setChromiumDisableWebSecurity(false);

// Webpack customizations
Config.overrideWebpackConfig((config) => {
  config.module?.rules?.push({
    test: /\.md$/,
    use: 'raw-loader',
  });
  return config;
});
```

## Testing

### Unit Testing

```bash
npm install @remotion/renderer --save-dev
```

```tsx
// test/MyVideo.test.tsx
import {render} from '@testing-library/react';
import {MyVideo} from '../src/MyVideo';

test('renders title', () => {
  const {getByText} = render(
    <MyVideo titleText="Test Title" titleColor="#000" logoUrl="" duration={5} />
  );
  expect(getByText('Test Title')).toBeInTheDocument();
});
```

### Visual Testing with Render Still

```bash
# Render specific frame for visual comparison
npx remotion still src/index.ts MyVideo --frame=150 test-snapshots/frame150.png
```

## Common Patterns

### Countdown Timer

```tsx
import {useCurrentFrame, useVideoConfig} from 'remotion';

const Countdown: React.FC<{seconds: number}> = ({seconds}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const remaining = Math.max(0, Math.ceil(seconds - frame / fps));

  return <div>{remaining}</div>;
};
```

### Loading Progress Bar

```tsx
const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const progress = frame / durationInFrames;

  return (
    <div
      style={{
        width: '100%',
        height: '10px',
        background: '#333',
      }}
    >
      <div
        style={{
          width: `${progress * 100}%`,
          height: '100%',
          background: '#0f0',
        }}
      />
    </div>
  );
};
```

### Typewriter Effect

```tsx
const Typewriter: React.FC<{text: string; speed: number}> = ({text, speed}) => {
  const frame = useCurrentFrame();
  const charsToShow = Math.floor(frame / speed);

  return <span>{text.slice(0, charsToShow)}</span>;
};
```

## Best Practices

1. **Keep components pure** - Same props should always produce same output
2. **Use memo for heavy calculations** inside components
3. **Preload assets** with `<Prefetch>` for smooth playback
4. **Test at different scales** - Preview at 0.5x, render at 1x
5. **Use sequences** to break videos into logical scenes
6. **Type your props** with Zod schemas for validation
7. **Handle async loading** with `useImage`, `useAudioData`, etc.

## Useful Packages

```bash
# Animation utilities
npm install remotion-animated

# Motion graphics presets
npm install @remotion/motion-graphics

# 3D (Three.js integration)
npm install @remotion/three

# Text animations
npm install @remotion/layout-utils

# Lambda rendering
npm install @remotion/lambda

# Stills (image generation)
npm install @remotion/stills

# Player (embeddable player)
npm install @remotion/player
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Black frames | Check component returns valid JSX |
| Out of memory | Reduce concurrency or use Lambda |
| Fonts not loading | Use `delayRender` and `continueRender` |
| Videos stutter | Preload with `<Prefetch>` |
| CORS errors | Add origins to `Config.setAllowedImageOrigins` |
| Slow renders | Enable `@remotion/renderer` multi-process |

## Resources

- Docs: https://www.remotion.dev/
- API Reference: https://www.remotion.dev/docs/
- Examples: https://github.com/remotion-dev/remotion/tree/main/packages/example
- Discord: https://remotion.dev/discord