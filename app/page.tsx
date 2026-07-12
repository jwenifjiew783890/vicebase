import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/home/Hero";
import StorySection from "@/components/home/StorySection";
import NewsSection from "@/components/home/NewsSection";
import FeaturedCreators from "@/components/home/FeaturedCreators";

export default function Home() {
  return (
    <>
      <Navbar />

      <main>
        <Hero />
        <StorySection />
        <NewsSection />
        <FeaturedCreators />
      </main>
    </>
  );
}