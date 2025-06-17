from manim import *

class SquareToCircle(Scene): 
    def construct(self):
        # Create a group to hold everything
        everything = VGroup()

        # Create first graph
        graph1 = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2, 2, 0.5],
            axis_config={"color": BLUE},
            x_length=8,  # Make the graph wider
            y_length=3,  # Control height
        ).scale(0.5).shift(UP*2.5)

        # Create second graph
        graph2 = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2, 2, 0.5],
            axis_config={"color": BLUE},
            x_length=8,  # Make the graph wider
            y_length=3,  # Control height
        ).scale(0.5)

        graph3 = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2, 2, 0.5],
            axis_config={"color": BLUE},
            x_length=8,  # Make the graph wider
            y_length=3,  # Control height
        ).scale(0.5).shift(DOWN*2.5)

        # Labels for first graph
        labels1 = [
            (0, "0"),
            (1/2, "1/2"),
            (1, "1"),
        ]
        
        # Labels for second graph
        labels2 = [
            (0, "0"),
            (1/2, "1/2"),
            (1, "1"),
        ]

        # Add labels to graphs
        for x, tex in labels1:
            label = MathTex(tex)
            label.scale(0.5)
            label.next_to(graph1.c2p(x, 0), DOWN)
            graph1.add(label)

        for x, tex in labels2:
            label = MathTex(tex)
            label.scale(0.5)
            label.next_to(graph2.c2p(x, 0), DOWN)
            graph2.add(label)

        # Create sine waves with different frequencies
        a1 = 10  # First frequency
        a2 = 5   # Second frequency
        sine_wave1 = graph1.plot(lambda x: np.sin(2*np.pi*a1*x), color=RED)
        sine_wave2 = graph2.plot(lambda x: np.sin(2*np.pi*a2*x), color=GREEN)
        wave3 = graph3.plot(lambda x: np.sin(2*np.pi*a1*x) + np.sin(2*np.pi*a2*x), color=YELLOW)

        # Create VGroups for labels to position them together
        text_labels1 = VGroup(
            MathTex(f"f_1 = {a1} Hz"),
            MathTex(f"T_1 = {1/a1} s")
        ).arrange(RIGHT, buff=0.3).scale(0.8).next_to(graph1, RIGHT, buff=0.3)

        text_labels2 = VGroup(
            MathTex(f"f_2 = {a2} Hz"),
            MathTex(f"T_2 = {1/a2} s")
        ).arrange(RIGHT, buff=0.3).scale(0.8).next_to(graph2, RIGHT, buff=0.3)

        text_labels3 = VGroup(
            MathTex("Composite"),
            MathTex("Wave")
        ).arrange(RIGHT, buff=0.3).scale(0.8).next_to(graph3, RIGHT, buff=0.3)

        # Add everything to the main group
        everything.add(graph1, graph2, graph3, sine_wave1, sine_wave2, wave3, text_labels1, text_labels2, text_labels3)
        
        # Shift everything left
        everything.shift(LEFT*2)

        # Animate everything
        self.play(
            Create(graph1),
            Create(graph2),
            Create(graph3)
        )
        self.play(
            Create(sine_wave1),
            Create(sine_wave2),
            Create(wave3),
            run_time=2
        )
        self.play(
            Write(text_labels1),
            Write(text_labels2),
            Write(text_labels3)
        )
        self.wait(5)

# Configure the scene settings
config.frame_width = 16  # Make the window wider
config.frame_height = 9  # 16:9 aspect ratio
config.pixel_width = 1920  # HD resolution
config.pixel_height = 1080