from env.footpong import footpong

if __name__ == "__main__":
    env = footpong()
    env.reset()
    env.render()

    done = False
    while not done:
    #    actions = {agent: env.action_space.sample() for agent in env.agents}
    #    _, _, done, _ = env.step(actions)
        env.render()

    env.close()
