import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { getOverview, predictPosting } from "./ml";

const postingSchema = z.object({
  job_title: z.string().optional(), location: z.string().optional(), industry: z.string().optional(), salary_range: z.string().optional(), company_profile: z.string().optional(), job_desc: z.string().optional(), skills_desc: z.string().optional(), employment_type: z.string().optional(), text: z.string().optional(),
});

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  model: router({
    overview: publicProcedure.query(() => getOverview()),
    predict: publicProcedure.input(postingSchema).mutation(({ input }) => predictPosting(input)),
  }),
});

export type AppRouter = typeof appRouter;
