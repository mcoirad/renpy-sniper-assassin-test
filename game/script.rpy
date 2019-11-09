init python:

    import math
    import pygame

    class Revealer(renpy.Displayable):

        def __init__(self, child, child2, child3, **kwargs):

            # Pass additional properties on to the renpy.Displayable
            # constructor.
            super(Revealer, self).__init__(**kwargs)

            # The children
            # Child1 is the image of the flashlight/scope
            # Child2 is the overall darkness, in this case all-black
            # Child3 is the background to be revealed, in this case all-transparent
            # (The real background is the imagemap)
            self.child = renpy.displayable(child)
            self.child2 = renpy.displayable(child2)
            self.child3 = renpy.displayable(child3)
            #self.child4 = renpy.displayable(animated_scope)

            # The width and height of us, and our children.
            self.width = 0
            self.height = 0

            x, y = pygame.mouse.get_pos()
            self.xpos = x
            self.ypos = y


        def render(self, width, height, st, at):

            # Create transforms for the children.
            # The only image we expect to move around is the flashlight/scope
            t1 = Transform(child=self.child, xpos = self.xpos, ypos = self.ypos)
            t2 = Transform(child=self.child2, xpos = 0, ypos = 0)
            t3 = Transform(child=self.child3, xalign = 0, yalign = 0)

            # AlphaBlend the transforms
            scope_view = AlphaBlend(t1,  t2, t3, alpha=True)

            # Create a render from the Alphablend.
            child_render = renpy.render(scope_view, width, height, st, at)

            # Create the render we will return.
            render = renpy.Render(self.width, self.height)

            # Blit (draw) the result to our render.
            render.blit(child_render, (0, 0))

            # Return the render.
            return render


        def event(self, ev, x, y, st, scope_dimensions = 400):

            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.firing = True

            # Offset the scope by half its height/width so the cursor is at the middle
            cursor_offset = scope_dimensions / 2

            # Logic to ensure the flashlight/scope stays put when cursor leaves the screen
            # After movement, updates the scopes position and redraws render
            if (x != self.xpos - cursor_offset or y != self.ypos - cursor_offset) and (x > 0 or y > 0):

                self.xpos = x - cursor_offset
                self.ypos = y - cursor_offset

                #self.ypos = self.ypos + self.animate_firing()

                renpy.redraw(self, 0)

            # Pass the event to our child.
            return self.child.event(ev, x, y, st)

        def visit(self):
            return [ self.child ]

image animated_scope:
    "scope"
    linear 1.0 yoffset -100
    pause 0.01
    linear 1.0 yoffset 100


screen sniper_minigame:

    modal True
    imagemap:

        # Instantiate flashlight/scope effect
        # Note: for clicking actions to take effect, the middle of scope image file needs to be black
        ground Revealer("scope", "black.png", "blank.png")

        # Example hotspots to show how actions might be taken
        hotspot (0,0,1920,1080) action (Hide("sniper_minigame"), Jump("did_not_break_window"))
        hotspot (1200,570,100,75) action (Hide("sniper_minigame"), Jump("broke_window"))



# Function for hiding the cursor during these scenes
init 1 python:
    def change_cursor(type="default"):
        persistent.mouse = type
        if type == "default":
            setattr(config, "mouse", None)
        elif type == "1":
            setattr(config, "mouse", {"default": [("images/empty_mouse.png", 0, 0)]})

    if not hasattr(persistent, "mouse"):
        change_cursor(1)
    else:
        change_cursor(persistent.mouse)


label start:

    # Hide Cursor
    $ change_cursor("1")
    $ is_shooting = False

    scene poor_neighborhood:
        xalign 0.5
        yalign 0.5
    "Break the car window!"
    show screen sniper_minigame
    "Shoot out the back right window of the car!"

    return

label broke_window:

    # Show broken window on top of background
    image window = "broken_window.png"
    show window:
        xpos 1200
        ypos 570

    # Reveal cursor
    $ change_cursor()
    "Broke the window."
    return

label did_not_break_window:
    "You missed."
    # Reveal cursor
    $ change_cursor()
    return
